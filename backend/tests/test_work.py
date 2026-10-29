import asyncio
import itertools
import json
import random
import string
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

import lark
import pytest
from django.contrib.contenttypes.models import ContentType

from otodb.api.common import ApiError, _parse_date_atom
from otodb.api.work import work_search_grammar
from otodb.common import process_video_info
from otodb.models import Comment, MediaWork, WorkSource
from otodb.models.enums import ErrorCode, Platform, Rating, WorkOrigin


def random_str(length):
	return ''.join(
		random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
	)


def get_video_infos_mock():
	json_path = Path(__file__).parent / 'mocks' / 'video_info.json'
	with json_path.open(encoding='utf-8') as f:
		info = json.load(f)
		return process_video_info(info), info


def fuzz_video_infos(info_tuple):
	full_info = info_tuple[1].copy()
	new_id = random_str(10)
	while new_id == full_info['id']:
		new_id = random_str(10)
	full_info['id'] = new_id
	full_info['title'] = random_str(10)
	full_info['description'] = random_str(20)
	full_info['timestamp'] = int(time.time())
	full_info['url'] = 'https://youtu.be/' + new_id
	return process_video_info(full_info), full_info


# Fixtures specific to work tests


@pytest.fixture
def base_video_info():
	"""Load base video info mock data."""
	return get_video_infos_mock()


@pytest.fixture
def video_info_mock(base_video_info):
	"""Create a mock for video_info with fuzzed data."""
	fuzzed = fuzz_video_infos(base_video_info)
	with patch('otodb.api.source.video_info') as mock:
		mock.return_value = fuzzed
		yield mock, fuzzed


@pytest.fixture
def add_source(async_source_client):
	"""Helper to create a source via the source API."""

	def _add(
		is_reupload=False,
		work_id: str | None = None,
		user=None,
	):
		query_params = {
			'url': 'https://youtu.be/fakeUrl',
			'is_reupload': is_reupload,
		}
		if work_id is not None:
			query_params['work_id'] = work_id

		return asyncio.run(
			async_source_client.post(
				'/source?' + urlencode(query_params),
				user=user,
			)
		)

	return _add


@pytest.fixture
def create_work(work_client):
	"""Helper to create a work from a source via the work API."""

	def _create(source_id, rating=0, tags=None, user=None):
		return work_client.post(
			'/create',
			data=json.dumps(
				{
					'source_id': source_id,
					'title': None,
					'description': None,
					'rating': rating,
					'tags': tags or [],
				}
			),
			content_type='application/json',
			user=user,
		)

	return _create


# Tests
@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestWork:
	"""Work-related tests."""

	def test_source_creation_does_not_create_work(
		self, member, video_info_mock, add_source
	):
		"""Sources are created independently; no work is created."""
		res = add_source(user=member)
		assert res.status_code == 200
		result = res.json()
		assert 'source_id' in result
		assert MediaWork.objects.count() == 0
		assert WorkSource.objects.count() == 1

	def test_editor_can_create_work_from_source(
		self, editor, video_info_mock, add_source, create_work
	):
		"""Editor creates source, then creates work from it."""
		res = add_source(user=editor)
		assert res.status_code == 200
		source_id = res.json()['source_id']

		res = create_work(source_id=source_id, user=editor)
		assert res.status_code == 200
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.filter(media__isnull=False).count() == 1

	def test_member_work_is_pending(
		self, member, video_info_mock, add_source, create_work
	):
		"""Member-created work has PENDING status."""
		from otodb.models.enums import Status

		res = add_source(user=member)
		source_id = res.json()['source_id']

		res = create_work(source_id=source_id, user=member)
		assert res.status_code == 200
		work = MediaWork.objects.get(pk=res.json())
		assert work.status == Status.PENDING

	def test_editor_work_is_approved(
		self, editor, video_info_mock, add_source, create_work
	):
		"""Editor-created work has APPROVED status."""
		from otodb.models.enums import Status

		res = add_source(user=editor)
		source_id = res.json()['source_id']

		res = create_work(source_id=source_id, user=editor)
		assert res.status_code == 200
		work = MediaWork.objects.get(pk=res.json())
		assert work.status == Status.APPROVED

	def test_bind_source_to_existing_work(
		self, member, editor, video_info_mock, add_source, create_work, base_video_info
	):
		"""Bind a new source to an existing work."""
		mock, v_info = video_info_mock

		# Editor creates first source + work
		res = add_source(user=editor)
		source_id = res.json()['source_id']
		res = create_work(source_id=source_id, user=editor)
		work_id = res.json()

		# New source with different video info
		mock.return_value = fuzz_video_infos(v_info)

		# Bind to existing work
		res = add_source(work_id=work_id, user=editor)
		assert res.status_code == 200
		assert res.json()['work_id'] == work_id
		assert WorkSource.objects.filter(media=work_id).count() == 2

	def test_source_already_bound_returns_work_id(
		self, editor, video_info_mock, add_source, create_work
	):
		"""Adding a source that already has a work returns the work_id."""
		res = add_source(user=editor)
		source_id = res.json()['source_id']
		res = create_work(source_id=source_id, user=editor)
		work_id = res.json()

		# Try adding the same URL again
		res = add_source(user=editor)
		assert res.status_code == 200
		assert res.json()['work_id'] == work_id

	def test_merge_preserves_comments(self, editor):
		"""Test that comments are migrated when works are merged."""
		work_1 = MediaWork.objects.create(title='Work 1', rating=Rating.GENERAL)
		work_2 = MediaWork.objects.create(title='Work 2', rating=Rating.GENERAL)
		work_source = WorkSource.objects.create(
			media=work_1,
			platform=Platform.YOUTUBE,
			source_id='test123',
			url='https://youtube.com/test123',
			published_date=date(2024, 1, 1),
			title='Test Source',
			added_by=editor,
		)

		mediawork_ct = ContentType.objects.get_for_model(MediaWork)

		comment_1 = Comment.objects.create(
			content_type=mediawork_ct,
			object_pk=work_1.pk,
		)
		comment_2 = Comment.objects.create(
			content_type=mediawork_ct,
			object_pk=work_2.pk,
		)

		MediaWork.merge(
			to_work=work_1,
			from_work=work_2,
			title='Merged Work',
			description='',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		comment_1.refresh_from_db()
		comment_2.refresh_from_db()
		assert comment_1.object_pk == work_1.pk
		assert comment_2.object_pk == work_1.pk

	def test_merge_preserves_comments_with_chain(self, editor):
		"""Test that comments are migrated correctly with chained merges."""
		work_1 = MediaWork.objects.create(title='Work 1', rating=Rating.GENERAL)
		work_2 = MediaWork.objects.create(title='Work 2', rating=Rating.GENERAL)
		work_3 = MediaWork.objects.create(title='Work 3', rating=Rating.GENERAL)

		work_source = WorkSource.objects.create(
			media=work_1,
			platform=Platform.YOUTUBE,
			source_id='test123',
			url='https://youtube.com/test123',
			published_date=date(2024, 1, 1),
			title='Test Source',
			added_by=editor,
		)

		mediawork_ct = ContentType.objects.get_for_model(MediaWork)

		comment_1 = Comment.objects.create(
			content_type=mediawork_ct,
			object_pk=work_2.pk,
		)
		comment_2 = Comment.objects.create(
			content_type=mediawork_ct,
			object_pk=work_3.pk,
		)

		MediaWork.merge(
			to_work=work_1,
			from_work=work_2,
			title='Merged Work',
			description='',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		MediaWork.merge(
			to_work=work_1,
			from_work=work_3,
			title='Merged Work',
			description='',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		comment_1.refresh_from_db()
		comment_2.refresh_from_db()
		assert comment_1.object_pk == work_1.pk
		assert comment_2.object_pk == work_1.pk

	def test_merge_always_uses_lowest_id(self, editor):
		"""Test that merge always keeps the lower ID work."""
		work_1 = MediaWork.objects.create(title='Work 1', rating=Rating.GENERAL)
		work_2 = MediaWork.objects.create(title='Work 2', rating=Rating.GENERAL)

		work_source = WorkSource.objects.create(
			media=work_1,
			platform=Platform.YOUTUBE,
			source_id='test123',
			url='https://youtube.com/test123',
			published_date=date(2024, 1, 1),
			title='Test Source',
			added_by=editor,
		)

		MediaWork.merge(
			to_work=work_2,
			from_work=work_1,
			title='Merged',
			description='',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		work_1.refresh_from_db()
		work_2.refresh_from_db()
		assert work_2.moved_to == work_1
		assert work_1.title == 'Merged'

	def test_merge_with_self_is_rejected(self, editor, work_client):
		"""Merging a work into itself must not point it at itself or drop its tags."""
		work = MediaWork.objects.create(title='Work', rating=Rating.GENERAL)
		work_source = WorkSource.objects.create(
			media=work,
			platform=Platform.YOUTUBE,
			source_id='test123',
			url='https://youtube.com/test123',
			published_date=date(2024, 1, 1),
			title='Test Source',
			added_by=editor,
		)

		with pytest.raises(ApiError) as exc_info:
			work_client.post(
				f'/merge?{urlencode({"from_work_id": work.pk, "to_work_id": work.pk})}',
				json={
					'title': 'Merged',
					'description': '',
					'thumbnail_source_id': work_source.pk,
					'rating': Rating.GENERAL,
				},
				user=editor,
			)
		assert exc_info.value.code == ErrorCode.CANNOT_MERGE_WITH_SELF

		with pytest.raises(ValueError):
			MediaWork.merge(
				to_work=work,
				from_work=work,
				title='Merged',
				description='',
				thumbnail_source=work_source,
				rating=Rating.GENERAL,
			)

		work.refresh_from_db()
		assert work.moved_to is None
		assert work.title == 'Work'


# Date metatags

NOW = datetime(2026, 10, 29, 12, 30, tzinfo=UTC)
W2 = NOW - timedelta(weeks=2)
Y1 = NOW - timedelta(days=365.25)


def _d(*args):
	return datetime(*args, tzinfo=UTC)


def parse_dates(tags):
	(value,) = work_search_grammar.parse(tags).find_data('date_range_value')
	return [_parse_date_atom(atom, NOW) for atom in value.children]


@pytest.mark.parametrize(
	'tags,expected',
	[
		('date:2010-03-15', [('gte', date(2010, 3, 15)), ('lt', date(2010, 3, 16))]),
		('date:>2010-03-15', [('gte', date(2010, 3, 16))]),
		('date:>=2010-03-15', [('gte', date(2010, 3, 15))]),
		('date:<2010-03-15', [('lt', date(2010, 3, 15))]),
		('date:<=2010-03-15', [('lt', date(2010, 3, 16))]),
		(
			'date:2010-03-15..2010-03-20',
			[('gte', date(2010, 3, 15)), ('lt', date(2010, 3, 21))],
		),
		(
			'date:2010-03-15...2010-03-20',
			[('gte', date(2010, 3, 15)), ('lt', date(2010, 3, 20))],
		),
		('date:2010-03-15..', [('gte', date(2010, 3, 15))]),
		('date:2010-03-15...', [('gte', date(2010, 3, 15))]),
		('date:..2010-03-20', [('lt', date(2010, 3, 21))]),
		('date:...2010-03-20', [('lt', date(2010, 3, 20))]),
		('date:2010-12-31', [('gte', date(2010, 12, 31)), ('lt', date(2011, 1, 1))]),
		('date:2012-02-29', [('gte', date(2012, 2, 29)), ('lt', date(2012, 3, 1))]),
		('age:<2w', [('gte', W2)]),
		('age:<=2w', [('gte', W2)]),
		('age:>2w', [('lt', W2)]),
		('age:>=2w', [('lt', W2)]),
		('age:2w..1y', [('gte', Y1), ('lt', W2)]),
		('age:2w..', [('lt', W2)]),
		('age:..2w', [('gte', W2)]),
		('age:2w', [('gte', _d(2026, 10, 15)), ('lt', _d(2026, 10, 16))]),
		('date:2010-01-01..1y', [('gte', date(2010, 1, 1)), ('lt', Y1)]),
	],
)
def test_date_value_bounds(tags, expected):
	assert parse_dates(tags) == [expected]


@pytest.mark.parametrize(
	'forward,backward',
	[
		('date:2010-03-15..2010-03-20', 'date:2010-03-20..2010-03-15'),
		('date:2010-03-15...2010-03-20', 'date:2010-03-20...2010-03-15'),
		('age:2w..1y', 'age:1y..2w'),
		('date:2010-01-01..1y', 'date:1y..2010-01-01'),
	],
)
def test_date_range_order_does_not_matter(forward, backward):
	assert parse_dates(forward) == parse_dates(backward)


@pytest.mark.parametrize(
	'value,delta',
	[
		('1s', timedelta(seconds=1)),
		('1sec', timedelta(seconds=1)),
		('1seconds', timedelta(seconds=1)),
		('1m', timedelta(minutes=1)),
		('1mi', timedelta(minutes=1)),
		('1min', timedelta(minutes=1)),
		('1h', timedelta(hours=1)),
		('1hr', timedelta(hours=1)),
		('1d', timedelta(days=1)),
		('1w', timedelta(weeks=1)),
		('1wk', timedelta(weeks=1)),
		('1mo', timedelta(days=365.25 / 12)),
		('1y', timedelta(days=365.25)),
		('1yr', timedelta(days=365.25)),
		('2years', timedelta(days=2 * 365.25)),
		('2W', timedelta(weeks=2)),
		('1.5d', timedelta(days=1.5)),
	],
)
def test_age_units(value, delta):
	assert parse_dates(f'age:<{value}') == [[('gte', NOW - delta)]]


def test_date_comma_list_mixes_forms():
	assert parse_dates('age:<1d,2010-01-01..2010-01-31') == [
		[('gte', NOW - timedelta(days=1))],
		[('gte', date(2010, 1, 1)), ('lt', date(2010, 2, 1))],
	]


@pytest.mark.parametrize('value', ['<2w', '2010-03-15', '1y..2010-01-01'])
def test_date_and_age_are_aliases(value):
	assert parse_dates(f'date:{value}') == parse_dates(f'age:{value}')


@pytest.mark.parametrize(
	'tags,error',
	[
		('date:2010-02-30', ValueError),
		('age:2xyz', ValueError),
		('age:3000y', OverflowError),
	],
)
def test_invalid_date_values_raise(tags, error):
	with pytest.raises(error):
		parse_dates(tags)


@pytest.mark.parametrize(
	'tags', ['date:2010', 'date:2010-03', 'age:2', 'id:2w', 'id:2010-03-15']
)
def test_malformed_date_values_do_not_parse(tags):
	with pytest.raises(lark.exceptions.UnexpectedInput):
		work_search_grammar.parse(tags)


@pytest.mark.parametrize('tags', ['id:5', 'duration:>=300', 'id:1...5'])
def test_int_ranges_still_parse(tags):
	assert any(work_search_grammar.parse(tags).find_data('range_value'))


@pytest.fixture
def search_ids(work_client):
	def _search(tags):
		res = work_client.get('/search?' + urlencode({'query': '', 'tags': tags}))
		assert res.status_code == 200
		return {int(w['id']) for w in res.json()['items']}

	return _search


@pytest.fixture
def make_work():
	def _make(created_at=None):
		work = MediaWork.objects.create(title='Work', rating=Rating.GENERAL)
		if created_at is not None:  # auto_now_add ignores a value passed to create()
			MediaWork.objects.filter(pk=work.pk).update(created_at=created_at)
		return work.pk

	return _make


@pytest.fixture
def make_source(member):
	ids = itertools.count()

	def _make(
		work_id,
		published_date,
		work_origin=WorkOrigin.AUTHOR,
		platform=Platform.YOUTUBE,
		published_at=None,
	):
		n = next(ids)
		return WorkSource.objects.create(
			media_id=work_id,
			platform=platform,
			source_id=f'date-test-{n}',
			url=f'https://youtu.be/date-test-{n}',
			published_date=published_date,
			published_at=published_at,
			work_origin=work_origin,
			added_by=member,
		)

	return _make


def test_date_day_boundaries(search_ids, make_work):
	before = make_work(_d(2010, 3, 14, 23, 59, 59))
	start = make_work(_d(2010, 3, 15))
	end = make_work(_d(2010, 3, 15, 23, 59, 59, 999999))
	after = make_work(_d(2010, 3, 16))
	assert search_ids('date:2010-03-15') == {start, end}
	assert search_ids('date:>2010-03-15') == {after}
	assert search_ids('date:<2010-03-15') == {before}
	assert search_ids('date:<=2010-03-15') == {before, start, end}
	assert search_ids('date:2010-03-14..2010-03-15') == {before, start, end}
	assert search_ids('date:2010-03-15...2010-03-16') == {start, end}


def test_age_compares_how_old(search_ids, make_work):
	now = datetime.now(UTC)
	hour = make_work(now - timedelta(hours=1))
	days = make_work(now - timedelta(days=10))
	old = make_work(now - timedelta(days=400))
	assert search_ids('age:<1d') == {hour}
	assert search_ids('age:>1w') == {days, old}
	assert search_ids('age:1w..1y') == {days}
	assert search_ids('age:1y..1w') == {days}
	assert search_ids('age:1w..') == {days, old}
	assert search_ids('age:..1w') == {hour}
	assert search_ids('age:1y..,<1d') == {hour, old}


def test_published_ignores_reuploads(search_ids, make_work, make_source):
	origin = make_work()
	make_source(origin, date(2010, 5, 1))
	reupload_only = make_work()
	make_source(reupload_only, date(2010, 5, 1), WorkOrigin.REUPLOAD)
	assert search_ids('published:2010-05-01') == {origin}


def test_published_uses_earliest_origin(search_ids, make_work, make_source):
	work = make_work()
	make_source(work, date(2010, 1, 1))
	make_source(work, date(2015, 6, 1))
	make_source(work, date(2005, 1, 1), WorkOrigin.REUPLOAD)
	assert search_ids('published:2015-06-01') == set()
	assert search_ids('published:2010-01-01') == {work}
	assert search_ids('published:<2008-01-01') == set()


def test_negated_published(search_ids, make_work, make_source):
	match = make_work()
	make_source(match, date(2010, 5, 1))
	other = make_work()
	make_source(other, date(2011, 1, 1))
	undated = make_work()
	make_source(undated, None)
	no_sources = make_work()
	make_source(None, date(2010, 5, 1))
	assert search_ids('-published:2010-05-01') == {other, undated, no_sources}


def test_published_relative(search_ids, make_work, make_source):
	recent = make_work()
	make_source(recent, datetime.now(UTC).date())
	old = make_work()
	make_source(old, date(2010, 1, 1))
	assert search_ids('published:<1w') == {recent}
	assert search_ids('published:>1w') == {old}


def test_published_first_origin_by_time(search_ids, make_work, make_source):
	# Niconico's upload came first, though its day in Japan is later than YouTube's
	work = make_work()
	make_source(
		work,
		date(2026, 10, 29),
		platform=Platform.NICONICO,
		published_at=_d(2026, 10, 28, 19, 0, 0),
	)
	make_source(work, date(2026, 10, 28), published_at=_d(2026, 10, 28, 19, 0, 22))
	assert search_ids('published:2026-10-29') == {work}
	assert search_ids('published:2026-10-28') == set()


def test_published_relative_uses_exact_time(search_ids, make_work, make_source):
	uploaded = datetime.now(UTC) - timedelta(hours=2)
	work = make_work()
	make_source(work, uploaded.date(), published_at=uploaded)
	assert search_ids('published:<1h') == set()
	assert search_ids('published:<3h') == {work}


@pytest.mark.parametrize(
	'tags', ['date:2010-02-30', 'age:2xyz', 'age:3000y', 'date:2010']
)
def test_bad_date_values_match_nothing(search_ids, make_work, tags):
	make_work()
	assert search_ids(tags) == set()
