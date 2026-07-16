"""DB-trigger revision system: capture, serialization parity, and fan-out.

Self-contained -- the ``revision_triggers`` fixture installs the codegen'd triggers for
every tracked model (validating that all 17 compile against the real schema) and lets
pytest-django's per-test transaction roll them back, so it needs no applied migration
and never pollutes the rest of the suite. Edits are raw SQL to prove that *any* writer
is captured (the property the ORM capture never had).
"""

from datetime import date

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import connection

from otodb.account.models import Account
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
from otodb.revision_db import db_revision
from otodb.revision_spec import TABLES

ROUTE = int(Route.WORKSOURCE_SET_ORIGIN)  # 62


@pytest.fixture
def revision_triggers(db):
	"""Install the codegen'd capture triggers for every tracked model."""
	with connection.cursor() as cursor:
		cursor.execute(generate_sql())
	yield


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

	with db_revision(user=member, message='set origin', route=ROUTE):
		with connection.cursor() as cursor:
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

	with db_revision(user=member, message='m', route=ROUTE):
		with connection.cursor() as cursor:
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

	with db_revision(user=member, message='del', route=ROUTE):
		with connection.cursor() as cursor:
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

	with db_revision(user=member, message='noop', route=ROUTE):
		with connection.cursor() as cursor:
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


# --- fan-out ---------------------------------------------------------------


@pytest.mark.django_db
def test_fan_out_notifies_and_keeps_subscription(revision_triggers, member, editor):
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	# editor is watching this source
	Subscription.objects.create(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	)

	with db_revision(user=member, message='edit', route=ROUTE):
		with connection.cursor() as cursor:
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
	with db_revision(user=member, message='edit again', route=ROUTE):
		with connection.cursor() as cursor:
			cursor.execute(
				'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T2', ws.id]
			)

	assert Notification.objects.filter(target_id=editor.pk).count() == 2


@pytest.mark.django_db
def test_fan_out_deletes_subscription_with_row(revision_triggers, member, editor):
	"""A subscription outlives any number of changes but not its row: subscribers are
	notified of the deletion, then the dead row's subscriptions are pruned -- including
	the actor's fresh auto-subscription to it."""
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	Subscription.objects.create(
		subscriber=editor, entity_type_id=ws_ct, entity_id=ws.id
	)

	with db_revision(user=member, message='delete', route=ROUTE):
		with connection.cursor() as cursor:
			cursor.execute('DELETE FROM otodb_worksource WHERE id = %s', [ws.id])

	rev = Revision.objects.get()
	assert list(Notification.objects.values_list('target_id', 'revision_id')) == [
		(editor.pk, rev.id)
	]
	assert not Subscription.objects.filter(
		entity_type_id=ws_ct, entity_id=ws.id
	).exists()


@pytest.mark.django_db
def test_fan_out_excludes_actor(revision_triggers, member):
	"""An actor watching their own edit isn't notified about it."""
	ws = _make_worksource(member)
	ws_ct = _ct('worksource')
	Subscription.objects.create(
		subscriber=member, entity_type_id=ws_ct, entity_id=ws.id
	)

	with db_revision(user=member, message='edit', route=ROUTE):
		with connection.cursor() as cursor:
			cursor.execute(
				'UPDATE otodb_worksource SET title = %s WHERE id = %s', ['T', ws.id]
			)

	assert Notification.objects.count() == 0


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
