"""DB-trigger revision system: capture, serialization parity, and finalization.

Self-contained -- the `revision_triggers` fixture installs the codegen'd triggers for
every tracked model (validating that all 17 compile against the real schema) and lets
pytest-django's per-test transaction roll them back, so it needs no applied migration
and never pollutes the rest of the suite. Edits are raw SQL to prove that *any* writer
is captured (the property the ORM capture never had).
"""

import threading
from contextlib import contextmanager
from datetime import date

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import DatabaseError, connection

from otodb import revision_db
from otodb.account.models import Account
from otodb.api.history import _is_new_q, get_rev_restored, revision_changes
from otodb.models import (
	MediaWork,
	Revision,
	RevisionChange,
	WorkSource,
)
from otodb.models.enums import Platform, Route, WorkOrigin, WorkStatus
from otodb.models.posts import Notification, Subscription
from otodb.models.revision import RevisionChangeEntity
from otodb.revision_codegen import generate_sql
from otodb.revision_spec import TABLES

ROUTE = int(Route.WORKSOURCE_SET_ORIGIN)  # 62


@pytest.fixture
def revision_triggers(db):
	"""Install the codegen'd capture triggers for every tracked model."""
	with connection.cursor() as cursor:
		cursor.execute(generate_sql())
	yield


def _commit():
	"""Fire the deferred triggers the way COMMIT does -- the test transaction never
	commits, so a Revision would otherwise never be finalized."""
	with connection.cursor() as cursor:
		cursor.execute('SET CONSTRAINTS ALL IMMEDIATE')
		cursor.execute('SET CONSTRAINTS ALL DEFERRED')


@contextmanager
def db_revision(**kwargs):
	"""The real db_revision, as the outermost transaction it is in production."""
	with revision_db.db_revision(**kwargs):
		yield
	_commit()


def _write_under(cursor, rev):
	"""Send the transaction's following writes to an already existing Revision -- a
	stand-in for an overlapping transaction that opened `rev` earlier and writes now."""
	cursor.execute("SELECT set_config('otodb.rev_id', %s, true)", [str(rev.id)])


def _ct(model: str) -> int:
	return ContentType.objects.get(app_label='otodb', model=model).id


def _make_worksource(member, media=None) -> WorkSource:
	ws = WorkSource.objects.create(
		added_by=member,
		platform=Platform.YOUTUBE,
		url='https://www.youtube.com/watch?v=abc',
		source_id='abc',
		work_origin=WorkOrigin.AUTHOR,
		work_status=WorkStatus.AVAILABLE,
		media=media,
	)
	Revision.objects.all().delete()  # clear the INSERT-triggered rows
	with connection.cursor() as cursor:
		# The txn-local otodb.rev_id still points at the revision just deleted (the
		# whole test is one transaction); reset it so a later unstamped write mints a
		# fresh revision instead of dangling on the deleted id.
		cursor.execute("SELECT set_config('otodb.rev_id', '', true)")
	return ws


def _changes() -> list[dict]:
	return list(
		RevisionChange.objects.values(
			'target_type_id',
			'target_id',
			'target_column',
			'target_value',
			'deleted',
			'restored',
		).order_by('target_column')
	)


def _entities() -> set:
	return set(
		RevisionChangeEntity.objects.values_list('entity_type_id', 'entity_id', 'route')
	)


def _sql_value(expr: str):
	with connection.cursor() as cursor:
		cursor.execute(f'SELECT {expr}')
		return cursor.fetchone()[0]


# --- capture ---------------------------------------------------------------


@pytest.mark.django_db
def test_update_captures_single_change(revision_triggers, member):
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')

	with (
		db_revision(user=member, message='set origin', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
			[int(WorkOrigin.REUPLOAD), ws.id],
		)

	rev = Revision.objects.get()
	assert rev.user_id == member.pk
	assert rev.message == 'set origin'
	assert _changes() == [
		{
			'target_type_id': ws_ct,
			'target_id': ws.id,
			'target_column': 'work_origin',
			'target_value': str(int(WorkOrigin.REUPLOAD)),
			'deleted': False,
			'restored': False,
		}
	]
	assert _entities() == {(ws_ct, ws.id, ROUTE)}  # media NULL -> self only


@pytest.mark.django_db
def test_update_with_media_emits_media_entity(revision_triggers, member):
	mw = MediaWork.objects.create(title='W', description='D', rating=0)
	ws = _make_worksource(member, media=mw)
	ws_ct, mw_ct = _ct('worksource'), _ct('mediawork')

	with (
		db_revision(user=member, message='m', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
			[int(WorkOrigin.REUPLOAD), ws.id],
		)

	assert _entities() == {(ws_ct, ws.id, ROUTE), (mw_ct, mw.id, ROUTE)}


@pytest.mark.django_db
def test_insert_captures_all_tracked_fields(revision_triggers, member):
	with db_revision(user=member, message='create', route=ROUTE):
		WorkSource.objects.create(
			added_by=member,
			platform=Platform.YOUTUBE,
			url='https://www.youtube.com/watch?v=xyz',
			source_id='xyz',
			work_origin=WorkOrigin.AUTHOR,
			work_status=WorkStatus.AVAILABLE,
		)

	captured = {
		c['target_column']: c['target_value']
		for c in RevisionChange.objects.values('target_column', 'target_value')
	}
	assert set(captured) == set(WorkSource.RevisionMeta.tracked_fields)
	assert captured['platform'] == '1'
	assert captured['work_origin'] == '0'
	assert captured['added_by'] == str(member.pk)
	assert captured['title'] is None
	assert captured['media'] is None


@pytest.mark.django_db
def test_delete_captures_marker(revision_triggers, member):
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')

	with (
		db_revision(user=member, message='del', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute('DELETE FROM otodb_worksource WHERE id = %s', [ws.id])

	assert _changes() == [
		{
			'target_type_id': ws_ct,
			'target_id': ws.id,
			'target_column': None,
			'target_value': None,
			'deleted': True,
			'restored': False,
		}
	]


@pytest.mark.django_db
def test_update_when_guard_skips_function(revision_triggers, member):
	"""An untracked-only write (moderation flags, tagulous counts, ...) must not even
	invoke the capture function. EXPLAIN ANALYZE reports each row trigger that fired;
	a WHEN guard evaluating false means the trigger is never queued, so it is absent.
	The tracked write doubles as proof that EXPLAIN does report the trigger when fired.
	"""
	ws = _make_worksource(member)

	def update_fires_trigger(set_clause, value) -> bool:
		with connection.cursor() as cursor:
			cursor.execute(
				f'EXPLAIN ANALYZE UPDATE otodb_worksource SET {set_clause} = %s'
				' WHERE id = %s',
				[value, ws.id],
			)
			plan = '\n'.join(row[0] for row in cursor.fetchall())
		return 'zz_otodb_worksource_capture_u' in plan

	assert not update_fires_trigger('is_pending', True)  # untracked -> skipped
	assert update_fires_trigger('title', 'T')  # tracked -> enters the function


@pytest.mark.django_db
def test_update_when_guard_installed_on_every_table(revision_triggers):
	"""Every tracked table's UPDATE trigger carries a WHEN qualification (pg_trigger
	.tgqual), so no table silently regresses to fire-on-every-write."""
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT c.relname, t.tgqual IS NOT NULL
			FROM pg_trigger t
			JOIN pg_class c ON c.oid = t.tgrelid
			WHERE t.tgname LIKE 'zz\\_otodb\\_%\\_capture\\_u'
			"""
		)
		guarded = dict(cursor.fetchall())
	assert set(guarded) == {spec['table'] for spec in TABLES}
	assert all(guarded.values()), f'unguarded UPDATE triggers: {guarded}'


@pytest.mark.django_db
def test_noop_update_creates_no_revision(revision_triggers, member):
	"""Lazy revision creation: a write with no real change makes neither a Revision nor
	a RevisionChange."""
	ws = _make_worksource(member)

	with (
		db_revision(user=member, message='noop', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
			[int(WorkOrigin.AUTHOR), ws.id],
		)

	assert Revision.objects.count() == 0
	assert RevisionChange.objects.count() == 0


# --- serialization parity (the codegen landmine) ---------------------------


@pytest.mark.django_db
def test_serialization_matches_python_str(revision_triggers):
	"""The generated per-type expressions reproduce Django value_to_string = str()."""
	assert _sql_value("CASE WHEN true THEN 'True' ELSE 'False' END") == str(True)
	assert _sql_value("CASE WHEN false THEN 'True' ELSE 'False' END") == str(False)
	# float8 column: PG float8::text drops the .0 that Python str() keeps, so the
	# generated expression re-appends it. (Literals are cast to float8 to match the
	# real bpm column type -- a bare 120.0 is numeric, whose ::text already has .0.)
	assert _sql_value(
		'CASE WHEN 120.0::float8 = trunc(120.0::float8) AND abs(120.0::float8) < 1e16'
		" THEN 120.0::float8::text || '.0' ELSE 120.0::float8::text END"
	) == str(120.0)
	assert _sql_value(
		'CASE WHEN 0.5::float8 = trunc(0.5::float8) AND abs(0.5::float8) < 1e16'
		" THEN 0.5::float8::text || '.0' ELSE 0.5::float8::text END"
	) == str(0.5)
	assert _sql_value("to_char(date '2024-01-05', 'YYYY-MM-DD')") == str(
		date(2024, 1, 5)
	)


# --- finalization ----------------------------------------------------------


@pytest.mark.django_db
def test_finalize_notifies_and_keeps_subscription(revision_triggers, member, editor):
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	# editor is watching this source
	Subscription.objects.create(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	)

	with (
		db_revision(user=member, message='edit', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
		)

	rev = Revision.objects.get()
	assert list(Notification.objects.values_list('target_id', 'revision_id')) == [
		(editor.pk, rev.id)
	]
	# the watch persists (not consumed by the notification) ...
	assert Subscription.objects.filter(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	).exists()
	# active actor auto-subscribed to the edited entity
	assert Subscription.objects.filter(
		subscriber=member, entity_type_id=ws_ct, entity_id=ws.id
	).exists()

	# ... so a second edit notifies again
	with (
		db_revision(user=member, message='edit again', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T2', ws.id]
		)

	assert Notification.objects.filter(target_id=editor.pk).count() == 2


@pytest.mark.django_db
def test_finalize_deletes_subscription_with_row(revision_triggers, member, editor):
	"""A subscription outlives any number of changes but not its row: subscribers are
	notified of the deletion, then the dead row's subscriptions are pruned -- including
	the actor's fresh auto-subscription to it."""
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	Subscription.objects.create(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	)

	with (
		db_revision(user=member, message='delete', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute('DELETE FROM otodb_worksource WHERE id = %s', [ws.id])

	rev = Revision.objects.get()
	assert list(Notification.objects.values_list('target_id', 'revision_id')) == [
		(editor.pk, rev.id)
	]
	assert not Subscription.objects.filter(
		entity_type_id=ws_ct, entity_id=ws.id
	).exists()


@pytest.mark.django_db
def test_finalize_excludes_actor(revision_triggers, member):
	"""An actor watching their own edit isn't notified about it."""
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	Subscription.objects.create(
		subscriber=member, entity_type_id=ws_ct, entity_id=ws.id
	)

	with (
		db_revision(user=member, message='edit', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
		)

	assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_finalize_needs_no_application_call(revision_triggers, member, editor):
	"""A hand-typed edit -- no db_revision, no stamp -- is finalized all the same: the
	work hangs off a deferred constraint trigger that Postgres fires at COMMIT."""
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	Subscription.objects.create(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	)

	with connection.cursor() as cursor:
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
		)
	assert Notification.objects.count() == 0  # deferred: nothing yet
	_commit()

	rev = Revision.objects.get()
	assert rev.user_id == Account.get_system().pk
	assert list(Notification.objects.values_list('target_id', 'revision_id')) == [
		(editor.pk, rev.id)
	]


# --- no-op pruning ----------------------------------------------------------


def _set_origin(ws, origin, message='edit'):
	"""One Revision setting work_origin -- used to lay down a column's baseline."""
	with (
		db_revision(user=None, message=message, route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
			[int(origin), ws.id],
		)


@pytest.mark.django_db
def test_prune_drops_change_reverted_within_revision(revision_triggers, member, editor):
	"""x -> y -> x inside one Revision changed nothing: no change row, no Revision, and
	nobody is notified or auto-subscribed."""
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	_set_origin(ws, WorkOrigin.REUPLOAD, 'baseline')
	Subscription.objects.create(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	)

	with (
		db_revision(user=member, message='flip', route=ROUTE),
		connection.cursor() as cursor,
	):
		for origin in (WorkOrigin.AUTHOR, WorkOrigin.REUPLOAD):
			cursor.execute(
				'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
				[int(origin), ws.id],
			)

	assert list(Revision.objects.values_list('message', flat=True)) == ['baseline']
	assert RevisionChange.objects.count() == 1
	assert RevisionChangeEntity.objects.count() == 1
	assert Notification.objects.count() == 0
	assert not Subscription.objects.filter(subscriber=member).exists()


@pytest.mark.django_db
def test_prune_keeps_real_changes_of_same_revision(revision_triggers, member):
	"""Only the reverted column is dropped; x -> y -> z keeps its final value."""
	ws = _make_worksource(member)
	_set_origin(ws, WorkOrigin.REUPLOAD, 'baseline')

	with (
		db_revision(user=member, message='mixed', route=ROUTE),
		connection.cursor() as cursor,
	):
		for origin, title in (
			(WorkOrigin.AUTHOR, 'T1'),
			(WorkOrigin.REUPLOAD, 'T2'),
		):
			cursor.execute(
				'UPDATE otodb_worksource SET work_origin = %s, title = %s WHERE id = %s',
				[int(origin), title, ws.id],
			)

	assert list(
		RevisionChange.objects.filter(rev__message='mixed').values_list(
			'target_column', 'target_value'
		)
	) == [('title', 'T2')]


@pytest.mark.django_db
def test_prune_keeps_revert_made_in_a_later_revision(revision_triggers, member):
	"""x -> y in one Revision and y -> x in the next are two real changes: a change is
	compared with the column's previous change row, not with every value it ever held."""
	ws = _make_worksource(member)
	_set_origin(ws, WorkOrigin.REUPLOAD, 'baseline')
	_set_origin(ws, WorkOrigin.AUTHOR, 'away')
	_set_origin(ws, WorkOrigin.REUPLOAD, 'back')

	assert list(
		RevisionChange.objects.order_by('id').values_list(
			'rev__message', 'target_value'
		)
	) == [
		('baseline', str(int(WorkOrigin.REUPLOAD))),
		('away', str(int(WorkOrigin.AUTHOR))),
		('back', str(int(WorkOrigin.REUPLOAD))),
	]


@pytest.mark.django_db
def test_prune_drops_null_round_trip(revision_triggers, member):
	"""NULL -> x -> NULL is a no-op too (alias-and-delete does this to aliased_to): NULLs
	compare equal here, which a plain = would not give."""
	with db_revision(user=member, message='create', route=ROUTE):
		ws = WorkSource.objects.create(
			added_by=member,
			platform=Platform.YOUTUBE,
			url='https://www.youtube.com/watch?v=nul',
			source_id='nul',
			work_origin=WorkOrigin.AUTHOR,
			work_status=WorkStatus.AVAILABLE,
		)  # its INSERT records title = NULL

	with (
		db_revision(user=member, message='round trip', route=ROUTE),
		connection.cursor() as cursor,
	):
		for title in ('T', None):
			cursor.execute(
				'UPDATE otodb_worksource SET title = %s WHERE id = %s', [title, ws.id]
			)

	assert list(Revision.objects.values_list('message', flat=True)) == ['create']
	assert RevisionChange.objects.count() == len(WorkSource.RevisionMeta.tracked_fields)


@pytest.mark.django_db
def test_previous_value_follows_write_order_not_revision_id(revision_triggers, member):
	"""Overlapping transactions can get their Revision ids in the opposite order to their
	writes to one row. Pruning and the history view both take a column's previous change
	row by change id, which follows the writes: neither change below is a no-op, and each
	reports the value it really replaced."""
	ws = _make_worksource(member)
	_set_origin(ws, WorkOrigin.REUPLOAD, 'baseline')
	first_id = Revision.objects.create(user=member, message='wrote second')
	second_id = Revision.objects.create(user=member, message='wrote first')

	with connection.cursor() as cursor:
		for rev, origin in (
			(second_id, WorkOrigin.AUTHOR),
			(first_id, WorkOrigin.REUPLOAD),
		):
			_write_under(cursor, rev)
			cursor.execute(
				'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
				[int(origin), ws.id],
			)
	_commit()

	def old_and_new(rev):
		[change] = revision_changes(None, rev.id)['changes']
		return change.old_value, change.target_value

	author, reupload = str(int(WorkOrigin.AUTHOR)), str(int(WorkOrigin.REUPLOAD))
	assert old_and_new(second_id) == (reupload, author)
	assert old_and_new(first_id) == (author, reupload)


@pytest.mark.django_db
def test_history_reads_follow_write_order_not_revision_id(revision_triggers, member):
	"""So do the history view's other questions -- was the row created here, what did a
	deleted row last hold, which Revision introduced an entity. The row below is created,
	edited and deleted under Revisions whose ids run the other way."""
	deletes, edits, creates = (
		Revision.objects.create(user=member, message=message)
		for message in ('deletes', 'edits', 'creates')
	)

	with connection.cursor() as cursor:
		_write_under(cursor, creates)
		ws = WorkSource.objects.create(
			added_by=member,
			platform=Platform.YOUTUBE,
			url='https://www.youtube.com/watch?v=ord',
			source_id='ord',
			work_origin=WorkOrigin.AUTHOR,
			work_status=WorkStatus.AVAILABLE,
		)
		_write_under(cursor, edits)
		cursor.execute(
			'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
			[int(WorkOrigin.REUPLOAD), ws.id],
		)
		_write_under(cursor, deletes)
		cursor.execute('DELETE FROM otodb_worksource WHERE id = %s', [ws.id])
	_commit()

	assert all(c.created for c in revision_changes(None, creates.id)['changes'])
	[edit] = revision_changes(None, edits.id)['changes']
	assert (edit.created, edit.old_value) == (False, str(int(WorkOrigin.AUTHOR)))
	[last_held] = revision_changes(None, deletes.id)['deleted_rows'].values()
	assert {c.column: c.value for c in last_held}['work_origin'] == str(
		int(WorkOrigin.REUPLOAD)
	)
	assert list(Revision.objects.filter(_is_new_q())) == [creates]


@pytest.mark.django_db
def test_revision_without_changes_is_deleted(revision_triggers, member):
	"""A Revision exists only to hold change rows: one made by hand with none goes at
	COMMIT, just like one pruned empty."""
	Revision.objects.create(user=member, message='by hand')
	_commit()

	assert not Revision.objects.exists()


@pytest.mark.django_db
def test_row_created_and_deleted_in_one_revision_leaves_no_trace(
	revision_triggers, member
):
	"""Nobody ever saw the row, so neither its INSERT changes nor a deleted marker are
	recorded -- and a rollback's restored-marker pointing at it goes too."""
	ws_ct = _ct('worksource')
	with db_revision(user=member, message='ephemeral', route=ROUTE):
		ws = WorkSource.objects.create(
			added_by=member,
			platform=Platform.YOUTUBE,
			url='https://www.youtube.com/watch?v=tmp',
			source_id='tmp',
			work_origin=WorkOrigin.AUTHOR,
			work_status=WorkStatus.AVAILABLE,
		)
		ws.title = 'edited before it died'
		ws.save()
		RevisionChange.objects.create(
			rev_id=Revision.objects.get().id,
			target_type_id=ws_ct,
			target_id=ws.id + 1000,  # the generation this row "restored"
			target_value=str(ws.id),
			restored=True,
		)
		ws.delete()

	assert Revision.objects.count() == 0
	assert RevisionChange.objects.count() == 0
	assert RevisionChangeEntity.objects.count() == 0


@pytest.mark.django_db
def test_created_and_deleted_row_something_was_restored_from_stays(
	revision_triggers, member
):
	"""A rollback can restore a row, drop the copy, then restore the row again: the second
	restored-marker hangs off the first copy. Forgetting that copy would cut the chain
	from the original to the live row, so it stays on record, deleted-marker and all."""
	ws_ct = _ct('worksource')
	original = 10_000  # the long-deleted row both copies restore

	def restored_copy(of, source_id):
		ws = WorkSource.objects.create(
			added_by=member,
			platform=Platform.YOUTUBE,
			url=f'https://www.youtube.com/watch?v={source_id}',
			source_id=source_id,
			work_origin=WorkOrigin.AUTHOR,
			work_status=WorkStatus.AVAILABLE,
		)
		RevisionChange.objects.create(
			rev_id=Revision.objects.get().id,
			target_type_id=ws_ct,
			target_id=of,
			target_value=str(ws.id),
			restored=True,
		)
		return ws

	with db_revision(user=member, message='restore twice', route=ROUTE):
		first = restored_copy(original, 'one')
		first_id = first.id
		first.delete()
		second = restored_copy(first_id, 'two')

	assert get_rev_restored(ws_ct, original) == second.id
	assert RevisionChange.objects.filter(
		target_type_id=ws_ct, target_id=first_id, deleted=True
	).exists()


@pytest.mark.django_db
def test_row_created_and_deleted_is_not_left_as_an_entity(revision_triggers, member):
	"""Another row's changes, written while it pointed at the short-lived row, name that
	row as an entity. Finalize drops those names -- or the actor would be subscribed, for
	good, to a work that never existed."""
	ws = _make_worksource(member)
	ws_ct, mw_ct = _ct('worksource'), _ct('mediawork')

	with db_revision(user=member, message='ephemeral work', route=ROUTE):
		mw = MediaWork.objects.create(title='tmp', description='', rating=0)
		ws.media = mw
		ws.save()
		# Cascades to the source, which Django deletes AFTER the work: its deleted-marker
		# names the work after the work itself is already gone.
		mw.delete()

	assert [(c['target_column'], c['deleted']) for c in _changes()] == [
		('media', False),
		(None, True),
	]
	assert {(ct, eid) for ct, eid, _route in _entities()} == {(ws_ct, ws.id)}
	assert not Subscription.objects.filter(entity_type_id=mw_ct).exists()


@pytest.mark.django_db
def test_row_without_history_edited_then_deleted_keeps_marker(
	revision_triggers, member
):
	"""The count guard: a legacy row (no change rows anywhere) edited and deleted in one
	Revision has rows for only the edited columns, not all of them, so it is not
	mistaken for a row created in this Revision and its deletion stays on record."""
	ws = _make_worksource(member)  # history wiped -> a legacy row

	with (
		db_revision(user=member, message='edit+delete', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
		)
		cursor.execute('DELETE FROM otodb_worksource WHERE id = %s', [ws.id])

	assert [(c['target_column'], c['deleted']) for c in _changes()] == [
		('title', False),
		(None, True),
	]


# --- attribution ------------------------------------------------------------


@pytest.mark.django_db
def test_unstamped_write_attributed_to_system_bot(revision_triggers, member):
	"""A tracked write with no db_revision stamp (scheduler jobs like prune_expired,
	raw SQL, data migrations) is attributed to the system bot instead of left
	authorless. The trigger hardcodes account id 1; comparing against get_system()
	also guards the invariant that the bot -- created first, by account migration
	0008 -- really holds that id."""
	WorkSource.objects.create(
		added_by=member,
		platform=Platform.YOUTUBE,
		url='https://www.youtube.com/watch?v=bot',
		source_id='bot',
		work_origin=WorkOrigin.AUTHOR,
		work_status=WorkStatus.AVAILABLE,
	)

	assert Revision.objects.get().user_id == Account.get_system().pk


# --- nesting ----------------------------------------------------------------


def _revisions() -> dict:
	"""(message, user id) -> changed columns, per Revision."""
	return {
		(rev.message, rev.user_id): sorted(
			rev.revisionchange_set.values_list('target_column', flat=True)
		)
		for rev in Revision.objects.all()
	}


@pytest.mark.django_db
def test_nested_block_is_its_own_revision_and_hands_the_stamp_back(
	revision_triggers, member, editor
):
	"""An inner db_revision is a Revision of its own; the outer block's writes after it
	go to the outer Revision again, under the outer user and message."""
	ws = _make_worksource(member)

	with (
		revision_db.db_revision(user=member, message='outer', route=ROUTE),
		connection.cursor() as cursor,
	):
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
		)
		with revision_db.db_revision(user=editor, message='inner', route=ROUTE):
			cursor.execute(
				'UPDATE otodb_worksource SET description = %s WHERE id = %s',
				['D', ws.id],
			)
		cursor.execute(
			'UPDATE otodb_worksource SET work_origin = %s WHERE id = %s',
			[int(WorkOrigin.REUPLOAD), ws.id],
		)
	_commit()

	assert _revisions() == {
		('outer', member.pk): ['title', 'work_origin'],
		('inner', editor.pk): ['description'],
	}


@pytest.mark.django_db
def test_nested_block_that_raises_leaves_the_outer_stamp(
	revision_triggers, member, editor
):
	"""The inner block's savepoint rollback takes its writes, its Revision and its stamp
	with it."""
	ws = _make_worksource(member)

	with (
		revision_db.db_revision(user=member, message='outer', route=ROUTE),
		connection.cursor() as cursor,
	):
		with (
			pytest.raises(RuntimeError),
			revision_db.db_revision(user=editor, message='inner', route=ROUTE),
		):
			cursor.execute(
				'UPDATE otodb_worksource SET description = %s WHERE id = %s',
				['D', ws.id],
			)
			raise RuntimeError
		cursor.execute(
			'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
		)
	_commit()

	assert _revisions() == {('outer', member.pk): ['title']}


# --- concurrency ------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_concurrent_finalizes_subscribing_to_the_same_entities_do_not_deadlock(member):
	"""Two requests by one user commit at once, and both auto-subscribe them to the same
	new works -- which the two Revisions name in opposite orders. Finalize inserts the
	subscriptions in one fixed order, so the second COMMIT just waits for the first;
	unordered, each would hold unique-index entries the other wants, and Postgres would
	kill one request as a deadlock. Real transactions on two connections, so this runs on
	the migration-installed triggers rather than the `revision_triggers` fixture."""
	count = 100
	works = MediaWork.objects.bulk_create(
		MediaWork(title=f'W{i}', description='', rating=0) for i in range(count)
	)

	def source_ids(tag):
		return [
			source.id
			for source in WorkSource.objects.bulk_create(
				WorkSource(
					added_by=member,
					media=work,
					platform=Platform.YOUTUBE,
					url=f'https://www.youtube.com/watch?v={tag}{i}',
					source_id=f'{tag}{i}',
					work_origin=WorkOrigin.AUTHOR,
					work_status=WorkStatus.AVAILABLE,
				)
				for i, work in enumerate(works)
			)
		]

	both_written = threading.Barrier(2)
	errors = []

	def request(ids):
		try:
			with (
				revision_db.db_revision(user=member.pk, message='edit', route=ROUTE),
				connection.cursor() as cursor,
			):
				for pk in ids:
					cursor.execute(
						'UPDATE otodb_worksource SET title = %s WHERE id = %s',
						['T', pk],
					)
				both_written.wait(timeout=30)
		except DatabaseError as error:
			errors.append(error)
		finally:
			connection.close()  # this thread's own connection

	threads = [
		threading.Thread(target=request, args=(ids,))
		for ids in (source_ids('a'), source_ids('b')[::-1])
	]
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join(timeout=60)

	assert errors == []
	# each request's own sources, plus the works they share
	assert Subscription.objects.filter(subscriber=member).count() == 3 * count
