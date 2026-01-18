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
from otodb.models.enums import Rating, WorkOrigin, Platform


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
def upload_src(work_client):
	"""Helper function to upload a source."""

	def _upload(
		is_reupload=False,
		rating=0,
		work_id: int | None = None,
		has_original: bool = False,
		user=None,
		metadata: dict | None = None,
	):
		# Query parameters
		query_params = {
			'url': 'https://youtu.be/fakeUrl',
			'is_reupload': is_reupload,
		}
		if rating is not None:
			query_params['rating'] = rating
		if work_id is not None:
			query_params['work_id'] = work_id
		if has_original:
			query_params['original_url'] = 'https://youtu.be/fakeUrl'

		# Request body with metadata (only if provided)
		return work_client.post(
			'/source?' + urlencode(query_params),
			data=json.dumps(metadata) if metadata else None,
			content_type='application/json' if metadata else None,
			user=user,
		)

	return _upload


# Tests
@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestWork:
	"""Work-related tests."""

	def test_must_not_create_work_for_source_if_member(
		self, member, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=member)
		assert res.status_code == 200
		assert res.json() is None

		vid1 = fuzz_video_infos(v_info)
		vid2 = fuzz_video_infos(v_info)
		mock.side_effect = [vid1, vid2]

		res = upload_src(user=member, has_original=True)
		assert res.status_code == 200
		assert res.json() is None

		assert MediaWork.objects.count() == 0
		assert WorkSource.objects.count() == 3

	def test_must_create_new_work_for_source_if_editor(
		self, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=editor)
		assert res.status_code == 200
		assert res.json() == 1

		vid1 = fuzz_video_infos(base_video_info)
		vid2 = fuzz_video_infos(base_video_info)
		mock.side_effect = [vid1, vid2]

		res = upload_src(user=editor, has_original=True)
		assert res.status_code == 200
		assert res.json() == 2

		assert MediaWork.objects.count() == 2
		assert WorkSource.objects.count() == 3

	def test_must_add_new_source_to_provided_work_id_ignoring_rating_as_member(
		self, member, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=editor)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 1

		mock.return_value = fuzz_video_infos(v_info)

		res = upload_src(work_id=1, user=member, rating=Rating.EXPLICIT)
		work = MediaWork.objects.get(pk=res.json())
		assert res.json() == 1
		assert work.rating == Rating.GENERAL
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 2

	def test_must_add_new_source_to_provided_work_id_updating_rating_as_editor(
		self, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=editor)
		assert res.json() == 1

		mock.return_value = fuzz_video_infos(v_info)

		res = upload_src(work_id=1, user=editor, rating=Rating.EXPLICIT)
		work = MediaWork.objects.get(pk=res.json())
		assert res.json() == 1
		assert work.rating == Rating.EXPLICIT
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 2

	def test_must_add_new_source_based_on_priority_as_member(
		self, member, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		vid1 = v_info
		vid2 = fuzz_video_infos(v_info)
		vid3 = fuzz_video_infos(v_info)

		mock.return_value = vid1
		res = upload_src(user=editor)
		assert res.json() == 1
		mock.return_value = vid2
		res = upload_src(user=editor)
		assert res.json() == 2

		mock.side_effect = [vid2, vid3]

		res = upload_src(work_id=1, is_reupload=True, has_original=True, user=member)
		assert res.json() == 1
		assert MediaWork.objects.count() == 2
		assert WorkSource.objects.filter(media=1).count() == 2
		assert WorkSource.objects.filter(media=2).count() == 1

	def test_must_add_to_work_id_as_member_if_provided_and_none_have_work(
		self, member, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=editor)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 1

		vid1 = fuzz_video_infos(v_info)
		vid2 = fuzz_video_infos(v_info)
		mock.side_effect = [vid1, vid2]

		res = upload_src(work_id=1, is_reupload=True, has_original=True, user=member)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.filter(media=1).count() == 3

	def test_must_add_to_reupload_if_only_it_has_work(
		self, member, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=editor)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 1

		vid1 = v_info
		vid2 = fuzz_video_infos(v_info)
		mock.side_effect = [vid1, vid2]

		res = upload_src(is_reupload=True, has_original=True, user=member)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 2

	def test_must_add_to_origin_work_if_only_it_has_work(
		self, member, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		res = upload_src(user=editor)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 1

		vid1 = fuzz_video_infos(v_info)
		vid2 = v_info
		mock.side_effect = [vid1, vid2]

		res = upload_src(is_reupload=True, has_original=True, user=member)
		assert res.json() == 1
		assert MediaWork.objects.count() == 1
		assert WorkSource.objects.count() == 2

	def test_must_redirect_to_relevant_work_ignoring_source_corrections_as_member(
		self, member, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		vid1 = v_info
		vid2 = fuzz_video_infos(v_info)

		res1 = upload_src(user=editor)
		mock.return_value = vid2
		res2 = upload_src(user=editor)

		mock.side_effect = [vid1, vid2, vid2]

		res3 = upload_src(is_reupload=True, has_original=True, user=member)
		workSource = WorkSource.objects.filter(source_id=vid1[0]['id']).first()
		assert workSource.work_origin == WorkOrigin.AUTHOR
		assert res3.json() == 1

		res4 = upload_src(user=member)
		assert res4.json() == 2

		assert MediaWork.objects.count() == 2
		assert WorkSource.objects.filter(media=res1.json()).count() == 1
		assert WorkSource.objects.filter(media=res2.json()).count() == 1

	def test_must_merge_to_reupload_applying_source_corrections_if_both_have_different_works_as_editor(
		self, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		vid1 = v_info
		vid2 = fuzz_video_infos(v_info)

		res1 = upload_src(user=editor)
		mock.return_value = vid2
		res2 = upload_src(user=editor, is_reupload=True)

		mock.side_effect = [vid1, vid2]

		res3 = upload_src(is_reupload=True, has_original=True, user=editor)
		workSource1 = WorkSource.objects.filter(source_id=vid1[0]['id']).first()
		workSource2 = WorkSource.objects.filter(source_id=vid2[0]['id']).first()
		assert workSource1.work_origin == WorkOrigin.REUPLOAD
		assert workSource2.work_origin == WorkOrigin.AUTHOR

		assert res3.json() == 1
		assert MediaWork.objects.count() == 2
		assert WorkSource.objects.filter(media=res1.json()).count() == 2
		assert WorkSource.objects.filter(media=res2.json()).count() == 0

	def test_must_merge_to_target_if_both_and_target_have_different_works_as_editor(
		self, editor, video_info_mock, upload_src, base_video_info
	):
		mock, v_info = video_info_mock
		vid2 = fuzz_video_infos(v_info)
		vid3 = fuzz_video_infos(v_info)

		res1 = upload_src(user=editor)
		mock.return_value = vid2
		res2 = upload_src(user=editor)
		mock.return_value = vid3
		res3 = upload_src(user=editor)

		mock.side_effect = [vid2, vid3]

		res4 = upload_src(
			is_reupload=True, has_original=True, work_id=res1.json(), user=editor
		)

		assert res4.json() == res1.json()
		assert MediaWork.objects.count() == 3
		assert WorkSource.objects.filter(media=res1.json()).count() == 3
		assert WorkSource.objects.filter(media=res2.json()).count() == 0
		assert WorkSource.objects.filter(media=res3.json()).count() == 0

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
			user=editor,
			comment='Comment on work 1',
		)
		comment_2 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_2.pk),
			site_id=1,
			user=editor,
			comment='Comment on work 2',
		)

		MediaWork.merge(
			to_work=work_1,
			from_work=work_2,
			title='Merged Work',
			description='Merged description',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		comment_1.refresh_from_db()
		comment_2.refresh_from_db()

		assert comment_1.object_pk == str(work_1.pk)
		assert comment_2.object_pk == str(work_1.pk)

		work_2.refresh_from_db()
		assert work_2.moved_to == work_1

		comments_on_work_1 = XtdComment.objects.filter(
			content_type=mediawork_ct, object_pk=str(work_1.pk)
		).count()
		comments_on_work_2 = XtdComment.objects.filter(
			content_type=mediawork_ct, object_pk=str(work_2.pk)
		).count()

		assert comments_on_work_1 == 2
		assert comments_on_work_2 == 0

	def test_merge_preserves_comments_with_chain(self, editor):
		"""Test that comments follow the moved_to chain correctly."""
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

		comment_2 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_2.pk),
			site_id=1,
			user=editor,
			comment='Comment on work 2',
		)
		comment_3 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_3.pk),
			site_id=1,
			user=editor,
			comment='Comment on work 3',
		)

		MediaWork.merge(
			to_work=work_2,
			from_work=work_3,
			title='Intermediate Work',
			description='',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		MediaWork.merge(
			to_work=work_1,
			from_work=work_2,
			title='Final Work',
			description='',
			thumbnail_source=work_source,
			rating=Rating.GENERAL,
		)

		comment_2.refresh_from_db()
		comment_3.refresh_from_db()

		assert comment_2.object_pk == str(work_1.pk)
		assert comment_3.object_pk == str(work_1.pk)

		comments_on_work_1 = XtdComment.objects.filter(
			content_type=mediawork_ct, object_pk=str(work_1.pk)
		).count()

		assert comments_on_work_1 == 2

	def test_merge_always_uses_lowest_id(self, editor):
		"""Test that merge always keeps the work with the lowest ID regardless of direction."""
		# Create works with explicit IDs (work_1 has lower ID)
		work_1 = MediaWork.objects.create(title='Work 1', rating=Rating.GENERAL)
		work_2 = MediaWork.objects.create(title='Work 2', rating=Rating.GENERAL)
		work_3 = MediaWork.objects.create(title='Work 3', rating=Rating.GENERAL)

		# Create sources for each work
		source_1 = WorkSource.objects.create(
			media=work_1,
			platform=Platform.YOUTUBE,
			source_id='test1',
			url='https://youtube.com/test1',
			published_date=date.today(),
			title='Source 1',
			added_by=editor,
		)
		source_2 = WorkSource.objects.create(
			media=work_2,
			platform=Platform.YOUTUBE,
			source_id='test2',
			url='https://youtube.com/test2',
			published_date=date.today(),
			title='Source 2',
			added_by=editor,
		)
		source_3 = WorkSource.objects.create(
			media=work_3,
			platform=Platform.YOUTUBE,
			source_id='test3',
			url='https://youtube.com/test3',
			published_date=date.today(),
			title='Source 3',
			added_by=editor,
		)

		# Create comments on each work
		mediawork_ct = ContentType.objects.get_for_model(MediaWork)
		comment_1 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_1.pk),
			site_id=1,
			user=editor,
			comment='Comment on work 1',
		)
		comment_2 = XtdComment.objects.create(
			content_type=mediawork_ct,
			object_pk=str(work_2.pk),
			site_id=1,
			user=editor,
			comment='Comment on work 2',
		)

		work_1_id = work_1.pk

		# Test 1: Merge work_2 -> work_1 (normal direction, to_work has lower ID)
		MediaWork.merge(
			to_work=work_1,
			from_work=work_2,
			title='Merged Title A',
			description='Merged Description A',
			thumbnail_source=source_1,
			rating=Rating.GENERAL,
		)

		work_1.refresh_from_db()
		work_2.refresh_from_db()
		source_2.refresh_from_db()
		comment_2.refresh_from_db()

		# Verify work_1 (lower ID) is preserved
		assert work_1.title == 'Merged Title A'
		assert work_1.description == 'Merged Description A'
		assert work_2.moved_to == work_1
		assert source_2.media == work_1
		assert comment_2.object_pk == str(work_1_id)

		# Test 2: Merge work_1 -> work_3 (reversed direction, from_work has lower ID)
		# This should swap internally so work_1 remains the target
		MediaWork.merge(
			to_work=work_3,
			from_work=work_1,
			title='Merged Title B',
			description='Merged Description B',
			thumbnail_source=source_1,
			rating=Rating.EXPLICIT,
		)

		work_1.refresh_from_db()
		work_3.refresh_from_db()
		source_1.refresh_from_db()
		source_3.refresh_from_db()
		comment_1.refresh_from_db()

		# Verify work_1 (lowest ID) is STILL preserved, not work_3
		assert work_1.title == 'Merged Title B'
		assert work_1.description == 'Merged Description B'
		assert work_1.rating == Rating.EXPLICIT
		assert work_3.moved_to == work_1
		assert work_1.moved_to is None  # work_1 should not be moved

		# All sources should now point to work_1
		assert source_1.media == work_1
		assert source_3.media == work_1

		# All comments should be on work_1
		assert comment_1.object_pk == str(work_1_id)

		# Verify all sources are on the lowest ID work
		assert WorkSource.objects.filter(media=work_1).count() == 3
		assert WorkSource.objects.filter(media=work_2).count() == 0
		assert WorkSource.objects.filter(media=work_3).count() == 0
