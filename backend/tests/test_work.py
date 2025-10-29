import json
import random
import string
import time
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

import pytest

from otodb.common import process_video_info
from otodb.models import MediaWork, WorkSource
from otodb.models.enums import Rating, WorkOrigin


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
	):
		payload = {
			'url': 'https://youtu.be/fakeUrl',
			'is_reupload': is_reupload,
		}
		if rating is not None:
			payload['rating'] = rating
		if work_id is not None:
			payload['work_id'] = work_id
		if has_original:
			payload['original_url'] = 'https://youtu.be/fakeUrl'

		return work_client.post(
			'/source?' + urlencode(payload),
			content_type='application/x-www-form-urlencoded',
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
