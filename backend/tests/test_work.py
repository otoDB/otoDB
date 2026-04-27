import json
import random
import string
import time
from datetime import date
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from django.contrib.contenttypes.models import ContentType
from django_comments_xtd.models import XtdComment

from otodb.common import process_video_info
from otodb.models import MediaWork, WorkSource
from otodb.models.enums import Platform, Rating


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
	with patch('otodb.models.work_source.video_info') as mock:
		mock.return_value = fuzzed
		yield mock, fuzzed


@pytest.fixture
def add_source(source_client):
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

		return source_client.post(
			'/source?' + urlencode(query_params),
			user=user,
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
			published_date=date.today(),
			title='Test Source',
			added_by=editor,
		)

		mediawork_ct = ContentType.objects.get_for_model(MediaWork)

		comment_1 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_1.pk),
			site_id=1,
		)
		comment_2 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_2.pk),
			site_id=1,
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
		assert comment_1.object_pk == str(work_1.pk)
		assert comment_2.object_pk == str(work_1.pk)

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
			published_date=date.today(),
			title='Test Source',
			added_by=editor,
		)

		mediawork_ct = ContentType.objects.get_for_model(MediaWork)

		comment_1 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_2.pk),
			site_id=1,
		)
		comment_2 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_3.pk),
			site_id=1,
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
		assert comment_1.object_pk == str(work_1.pk)
		assert comment_2.object_pk == str(work_1.pk)

	def test_merge_always_uses_lowest_id(self, editor):
		"""Test that merge always keeps the lower ID work."""
		work_1 = MediaWork.objects.create(title='Work 1', rating=Rating.GENERAL)
		work_2 = MediaWork.objects.create(title='Work 2', rating=Rating.GENERAL)

		work_source = WorkSource.objects.create(
			media=work_1,
			platform=Platform.YOUTUBE,
			source_id='test123',
			url='https://youtube.com/test123',
			published_date=date.today(),
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
