"""Trigger-maintained tag usage counts (`TagWork.count` / `TagSong.count`).

The column is the number of rows in the tag's instance table, kept by Postgres AFTER
row triggers on `otodb_tagworkinstance` / `otodb_tagsonginstance` (otodb/db_triggers.py)
so it is right for every writer -- ORM, raw SQL, M2M managers, cascades -- and is never
written from Python. The autouse fixture installs the SQL explicitly (CREATE OR REPLACE,
so it is idempotent over the post_migrate install) and pytest-django's per-test
transaction rolls everything back. Python objects are never updated by a trigger, so
every assertion reads the count back with `refresh_from_db()`.
"""

from contextlib import contextmanager
from io import StringIO

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import CommandError, call_command, get_commands
from django.db import connection

from otodb import revision_db
from otodb.db_triggers import generate_sql
from otodb.models import (
	MediaSong,
	MediaWork,
	RevisionChange,
	TagSong,
	TagSongInstance,
	TagWork,
	TagWorkInstance,
)
from otodb.models.enums import Route, WorkTagCategory

pytestmark = pytest.mark.django_db

TRIGGERS = {
	'otodb_tagworkinstance_count_i': 'otodb_tagworkinstance',
	'otodb_tagworkinstance_count_d': 'otodb_tagworkinstance',
	'otodb_tagworkinstance_count_u': 'otodb_tagworkinstance',
	'otodb_tagsonginstance_count_i': 'otodb_tagsonginstance',
	'otodb_tagsonginstance_count_d': 'otodb_tagsonginstance',
	'otodb_tagsonginstance_count_u': 'otodb_tagsonginstance',
}
FUNCTIONS = {'otodb_tagwork_count', 'otodb_tagsong_count'}


@pytest.fixture(autouse=True)
def db_triggers(db):
	"""Install every trigger (same SQL the post_migrate hook runs)."""
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


def _count(tag) -> int:
	tag.refresh_from_db()
	return tag.count


def _make_song(name: str) -> MediaSong:
	work_tag = TagWork.objects.create(name=name, category=WorkTagCategory.SONG)
	return MediaSong.objects.create(work_tag=work_tag, title=name, author='author')


# --- installation -----------------------------------------------------------


def test_triggers_installed_ocount_tables():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT t.tgname, c.relname
			FROM pg_trigger t
			JOIN pg_class c ON c.oid = t.tgrelid
			WHERE t.tgname = ANY(%s)
			""",
			[sorted(TRIGGERS)],
		)
		assert dict(cursor.fetchall()) == TRIGGERS
		cursor.execute(
			'SELECT proname FROM pg_proc WHERE proname = ANY(%s)', [sorted(FUNCTIONS)]
		)
		assert {row[0] for row in cursor.fetchall()} == FUNCTIONS


# --- work tags --------------------------------------------------------------


def test_orm_insert_and_delete():
	work = MediaWork.objects.create(title='count orm')
	tag = TagWork.objects.create(name='count orm tag')
	assert _count(tag) == 0

	twi = TagWorkInstance.objects.create(work=work, work_tag=tag)
	assert _count(tag) == 1

	twi.delete()
	assert _count(tag) == 0


def test_m2m_add_and_remove():
	work = MediaWork.objects.create(title='count m2m')
	tag = TagWork.objects.create(name='count m2m tag')

	work.tags.add(tag)
	assert _count(tag) == 1
	assert list(work.tags.all()) == [tag]

	work.tags.remove(tag)
	assert _count(tag) == 0
	assert not work.tags.exists()


def test_fk_update_moves_count_between_tags():
	work = MediaWork.objects.create(title='count move')
	t1 = TagWork.objects.create(name='count move one')
	t2 = TagWork.objects.create(name='count move two')
	twi = TagWorkInstance.objects.create(work=work, work_tag=t1)
	assert (_count(t1), _count(t2)) == (1, 0)

	twi.work_tag = t2
	twi.save()

	assert (_count(t1), _count(t2)) == (0, 1)


def test_non_fk_update_leaves_count_alone():
	work = MediaWork.objects.create(title='count same fk')
	tag = TagWork.objects.create(name='count same fk tag')
	twi = TagWorkInstance.objects.create(work=work, work_tag=tag)

	# Model.save() writes every column, the unchanged FK included: the UPDATE OF
	# trigger fires, but a same-value FK must not move anything.
	twi.used_as_source = True
	twi.save()
	assert _count(tag) == 1

	TagWorkInstance.objects.filter(pk=twi.pk).update(used_as_source=False)
	assert _count(tag) == 1


def test_raw_sql_writer_is_counted():
	"""Any writer, not just the ORM."""
	work = MediaWork.objects.create(title='count raw')
	tag = TagWork.objects.create(name='count raw tag')

	with connection.cursor() as cursor:
		cursor.execute(
			'INSERT INTO otodb_tagworkinstance'
			' (work_id, work_tag_id, used_as_source, creator_roles)'
			' VALUES (%s, %s, false, NULL)',
			[work.pk, tag.pk],
		)
	assert _count(tag) == 1

	with connection.cursor() as cursor:
		cursor.execute(
			'DELETE FROM otodb_tagworkinstance WHERE work_id = %s AND work_tag_id = %s',
			[work.pk, tag.pk],
		)
	assert _count(tag) == 0


def test_work_delete_cascades_instances_and_records_their_deletion(member):
	"""Django's collector cascades the instance rows (tagulous used to clear the M2M in
	a pre_delete hook): the counts fall back to 0 and the capture triggers still record
	one deleted-marker per instance row under the deleting Revision."""
	work = MediaWork.objects.create(title='count cascade')
	t1 = TagWork.objects.create(name='count cascade one')
	t2 = TagWork.objects.create(name='count cascade two')
	work.tags.add(t1, t2)
	instance_ids = sorted(
		TagWorkInstance.objects.filter(work=work).values_list('id', flat=True)
	)
	assert len(instance_ids) == 2
	assert (_count(t1), _count(t2)) == (1, 1)
	twi_ct = ContentType.objects.get(app_label='otodb', model='tagworkinstance').id

	with db_revision(
		user=member, message='delete work', route=int(Route.MEDIAWORK_DELETE)
	):
		work.delete()

	assert not TagWorkInstance.objects.filter(id__in=instance_ids).exists()
	assert (_count(t1), _count(t2)) == (0, 0)
	assert (
		sorted(
			RevisionChange.objects.filter(
				rev__message='delete work', target_type_id=twi_ct, deleted=True
			).values_list('target_id', flat=True)
		)
		== instance_ids
	)


def test_alias_moves_count_to_target():
	work = MediaWork.objects.create(title='count alias')
	a = TagWork.objects.create(name='count alias from')
	b = TagWork.objects.create(name='count alias into')
	work.tags.add(a)
	assert _count(a) == 1

	# `a` and `b` still hold count == 0 in memory; alias() saves both.
	TagWork.alias([a], b)

	assert _count(b) == 1
	assert _count(a) == 0
	assert not TagWorkInstance.objects.filter(work_tag=a).exists()
	assert TagWorkInstance.objects.filter(work=work, work_tag=b).exists()
	assert a.aliased_to_id == b.pk


def test_stale_save_does_not_clobber_count():
	work = MediaWork.objects.create(title='count stale')
	tag = TagWork.objects.create(name='count stale tag')
	TagWorkInstance.objects.create(work=work, work_tag=tag)
	assert tag.count == 0  # the Python object never learns of the trigger

	tag.category = WorkTagCategory.CREATOR
	tag.save()

	tag.refresh_from_db()
	assert tag.category == WorkTagCategory.CREATOR
	assert tag.count == 1


# --- song tags --------------------------------------------------------------


def test_song_instance_insert_update_delete():
	song = _make_song('count song')
	t1 = TagSong.objects.create(name='count song one')
	t2 = TagSong.objects.create(name='count song two')

	tsi = TagSongInstance.objects.create(song=song, song_tag=t1)
	assert (_count(t1), _count(t2)) == (1, 0)

	tsi.song_tag = t2
	tsi.save()
	assert (_count(t1), _count(t2)) == (0, 1)

	tsi.delete()
	assert (_count(t1), _count(t2)) == (0, 0)

	song.tags.add(t1)
	assert _count(t1) == 1
	song.tags.remove(t1)
	assert _count(t1) == 0


def test_song_merge_keeps_counts_consistent():
	to_song = _make_song('count merge to')
	from_song = _make_song('count merge from')
	shared = TagSong.objects.create(name='count merge shared')
	only_from = TagSong.objects.create(name='count merge only from')
	to_song.tags.add(shared)
	from_song.tags.add(shared, only_from)
	assert (_count(shared), _count(only_from)) == (2, 1)

	MediaSong.merge(to_song=to_song, from_song=from_song)

	assert not MediaSong.objects.filter(pk=from_song.pk).exists()
	assert set(to_song.tags.values_list('pk', flat=True)) == {shared.pk, only_from.pk}
	# the duplicate `shared` row went; `only_from` moved over
	assert (_count(shared), _count(only_from)) == (1, 1)
	for tag in (shared, only_from):
		assert _count(tag) == TagSongInstance.objects.filter(song_tag=tag).count()


# --- backfill ---------------------------------------------------------------


BACKFILL = 'TEMP_backfill_tag_counts'


def _backfill(*args):
	call_command(BACKFILL, *args, stdout=StringIO(), stderr=StringIO())


@pytest.mark.skipif(
	BACKFILL not in get_commands(), reason='one-off command not present'
)
def test_backfill_repairs_corrupted_counts():
	work = MediaWork.objects.create(title='count backfill')
	tag = TagWork.objects.create(name='count backfill tag')
	work.tags.add(tag)
	song = _make_song('count backfill song')
	song_tag = TagSong.objects.create(name='count backfill song tag')
	song.tags.add(song_tag)
	_backfill('--check')  # consistent: passes

	TagWork.objects.filter(pk=tag.pk).update(count=99)
	TagSong.objects.filter(pk=song_tag.pk).update(count=99)

	with pytest.raises(CommandError):
		_backfill('--check')
	assert (_count(tag), _count(song_tag)) == (99, 99)  # --check writes nothing

	_backfill()
	assert (_count(tag), _count(song_tag)) == (1, 1)
	_backfill('--check')


# --- endpoints --------------------------------------------------------------


def _items(response) -> list[tuple[str, int]]:
	assert response.status_code == 200
	return [(item['slug'], item['n_instance']) for item in response.json()['items']]


def test_search_orders_by_count_and_hides_orphans(tag_client):
	two = TagWork.objects.create(name='zeta two')
	one = TagWork.objects.create(name='zeta one')
	TagWork.objects.create(name='zeta none')
	for i in range(2):
		MediaWork.objects.create(title=f'zeta work {i}').tags.add(two)
	MediaWork.objects.create(title='zeta work 2').tags.add(one)

	assert _items(tag_client.get('/search?query=zeta&order=count')) == [
		('zeta_two', 2),
		('zeta_one', 1),
	]
	assert _items(
		tag_client.get('/search?query=zeta&order=count&hide_orphans=false')
	) == [
		('zeta_two', 2),
		('zeta_one', 1),
		('zeta_none', 0),
	]


def test_search_autocomplete_collapses_alias_group_with_target_count(tag_client):
	base = TagWork.objects.create(name='omega base')
	alias = TagWork.objects.create(name='omega alias')
	alias.aliased_to = base
	alias.save()
	MediaWork.objects.create(title='omega work').tags.add(base)
	assert (_count(base), _count(alias)) == (1, 0)

	# only the alias matches its own slug; it carries the base's count
	assert _items(tag_client.get('/search?query=omega_alias&autocomplete=true')) == [
		('omega_alias', 1)
	]
	# both match: the group collapses to one suggestion
	assert _items(tag_client.get('/search?query=omega&autocomplete=true')) == [
		('omega_base', 1)
	]


def test_song_tag_search_reports_counts(tag_client):
	song = _make_song('sigma song')
	used = TagSong.objects.create(name='sigma used')
	TagSong.objects.create(name='sigma unused')
	song.tags.add(used)

	assert _items(tag_client.get('/song_tag_search?query=sigma')) == [
		('sigma_used', 1),
		('sigma_unused', 0),
	]
