from django.test import TestCase
from ninja.testing import TestClient
from otodb.api.work import work_router
from otodb.account.models import Account
from otodb.models import WorkSource, MediaWork
from otodb.models.enums import Rating, WorkOrigin
from urllib.parse import urlencode
from unittest.mock import patch
from otodb.common import process_video_info
from pathlib import Path
import json
import random
import string
import time


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


class WorkTest(TestCase):
	reset_sequences = True
	@classmethod
	def setUpTestData(self):
		self.v_info = get_video_infos_mock()

	def setUp(self):
		self.patcher = patch('otodb.models.work_source.video_info')
		self.mock_video_info = self.patcher.start()
		self.addCleanup(self.patcher.stop)

		fuzzed = fuzz_video_infos(self.v_info)
		self.mock_video_info.return_value = fuzzed
		self.v_info = fuzzed

		self.member = Account.objects.create_user(
			'user', 'user@test.com', password='user_pass', level=Account.Levels.MEMBER
		)
		self.editor = Account.objects.create_user(
			'editor',
			'editor@test.com',
			password='editor_pass',
			level=Account.Levels.EDITOR,
		)
		self.client = TestClient(work_router)

	def upload_src(
		self,
		is_reupload=False,
		rating=0,
		work_id: int | None = None,
		has_original: bool = False,
		user=None,
	):
		payload = {
			# Url does not matter, as the work ID is determined by infos
			# extracted by yt-dlp
			'url': 'https://youtu.be/fakeUrl',
			'is_reupload': is_reupload,
		}
		if rating is not None:
			payload['rating'] = rating
		if work_id is not None:
			payload['work_id'] = work_id
		if has_original:
			payload['original_url'] = 'https://youtu.be/fakeUrl'

		return self.client.post(
			'/source?' + urlencode(payload),
			content_type='application/x-www-form-urlencoded',
			user=user,
		)

	def test_must_not_create_work_for_source_if_member(self):
		res = self.upload_src(user=self.member)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json(), None)

		vid1 = fuzz_video_infos(self.v_info)
		vid2 = fuzz_video_infos(self.v_info)
		self.mock_video_info.side_effect = [vid1, vid2]

		res = self.upload_src(user=self.member, has_original=True)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json(), None)

		self.assertEqual(MediaWork.objects.all().count(), 0)
		self.assertEqual(WorkSource.objects.all().count(), 3)

	def test_must_create_new_work_for_source_if_editor(self):
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json(), 1)

		vid1 = fuzz_video_infos(self.v_info)
		vid2 = fuzz_video_infos(self.v_info)
		self.mock_video_info.side_effect = [vid1, vid2]

		res = self.upload_src(user=self.editor, has_original=True)
		self.assertEqual(res.status_code, 200)
		self.assertEqual(res.json(), 2)

		self.assertEqual(MediaWork.objects.all().count(), 2)
		self.assertEqual(WorkSource.objects.all().count(), 3)

	def test_must_add_new_source_to_provided_work_id_ignoring_rating_as_member(self):
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 1)

		self.mock_video_info.return_value = fuzz_video_infos(self.v_info)

		res = self.upload_src(work_id=1, user=self.member, rating=Rating.EXPLICIT)
		work = MediaWork.objects.get(pk=res.json())
		self.assertEqual(res.json(), 1)
		self.assertEqual(work.rating, Rating.GENERAL)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 2)

	def test_must_add_new_source_to_provided_work_id_updating_rating_as_editor(self):
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 1)

		self.mock_video_info.return_value = fuzz_video_infos(self.v_info)

		res = self.upload_src(work_id=1, user=self.editor, rating=Rating.EXPLICIT)
		work = MediaWork.objects.get(pk=res.json())
		self.assertEqual(res.json(), 1)
		self.assertEqual(work.rating, Rating.EXPLICIT)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 2)

	def test_must_add_new_source_based_on_priority_as_member(self):
		vid1 = self.v_info
		vid2 = fuzz_video_infos(self.v_info)
		vid3 = fuzz_video_infos(self.v_info)

		self.mock_video_info.return_value = vid1
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 1)
		self.mock_video_info.return_value = vid2
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 2)

		self.mock_video_info.side_effect = [vid2, vid3]

		res = self.upload_src(
			work_id=1, is_reupload=True, has_original=True, user=self.member
		)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 2)
		self.assertEqual(WorkSource.objects.filter(media=1).count(), 2)
		self.assertEqual(WorkSource.objects.filter(media=2).count(), 1)

	def test_must_add_to_work_id_as_member_if_provided_and_none_have_work(self):
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 1)

		vid1 = fuzz_video_infos(self.v_info)
		vid2 = fuzz_video_infos(self.v_info)
		self.mock_video_info.side_effect = [vid1, vid2]

		res = self.upload_src(
			work_id=1, is_reupload=True, has_original=True, user=self.member
		)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.filter(media=1).count(), 3)

	def test_must_add_to_reupload_if_only_it_has_work(self):
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 1)

		vid1 = self.v_info
		vid2 = fuzz_video_infos(self.v_info)
		self.mock_video_info.side_effect = [vid1, vid2]

		res = self.upload_src(is_reupload=True, has_original=True, user=self.member)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 2)

	def test_must_add_to_origin_work_if_only_it_has_work(self):
		res = self.upload_src(user=self.editor)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 1)

		vid1 = fuzz_video_infos(self.v_info)
		vid2 = self.v_info
		self.mock_video_info.side_effect = [vid1, vid2]

		res = self.upload_src(is_reupload=True, has_original=True, user=self.member)
		self.assertEqual(res.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 1)
		self.assertEqual(WorkSource.objects.all().count(), 2)

	def test_must_redirect_to_relevant_work_ignoring_source_corrections_as_member(self):
		vid1 = self.v_info
		vid2 = fuzz_video_infos(self.v_info)

		res1 = self.upload_src(user=self.editor)
		self.mock_video_info.return_value = vid2
		res2 = self.upload_src(user=self.editor)

		self.mock_video_info.side_effect = [vid1, vid2, vid2]

		res3 = self.upload_src(is_reupload=True, has_original=True, user=self.member)
		workSource = WorkSource.objects.filter(source_id=vid1[0]['id']).first()
		self.assertEqual(workSource.work_origin, WorkOrigin.AUTHOR)
		self.assertEqual(res3.json(), 1)

		res4 = self.upload_src(user=self.member)
		self.assertEqual(res4.json(), 2)

		self.assertEqual(MediaWork.objects.all().count(), 2)
		self.assertEqual(WorkSource.objects.filter(media=res1.json()).count(), 1)
		self.assertEqual(WorkSource.objects.filter(media=res2.json()).count(), 1)

	def test_must_merge_to_reupload_applying_source_corrections_if_both_have_different_works_as_editor(
		self,
	):
		vid1 = self.v_info
		vid2 = fuzz_video_infos(self.v_info)

		res1 = self.upload_src(user=self.editor)
		self.mock_video_info.return_value = vid2
		res2 = self.upload_src(user=self.editor, is_reupload=True)

		self.mock_video_info.side_effect = [vid1, vid2]

		res3 = self.upload_src(is_reupload=True, has_original=True, user=self.editor)
		workSource1 = WorkSource.objects.filter(source_id=vid1[0]['id']).first()
		workSource2 = WorkSource.objects.filter(source_id=vid2[0]['id']).first()
		self.assertEqual(workSource1.work_origin, WorkOrigin.REUPLOAD)
		self.assertEqual(workSource2.work_origin, WorkOrigin.AUTHOR)

		self.assertEqual(res3.json(), 1)
		self.assertEqual(MediaWork.objects.all().count(), 2)
		self.assertEqual(WorkSource.objects.filter(media=res1.json()).count(), 2)
		self.assertEqual(WorkSource.objects.filter(media=res2.json()).count(), 0)

	def test_must_merge_to_target_if_both_and_target_have_different_works_as_editor(
		self,
	):
		vid2 = fuzz_video_infos(self.v_info)
		vid3 = fuzz_video_infos(self.v_info)

		res1 = self.upload_src(user=self.editor)
		self.mock_video_info.return_value = vid2
		res2 = self.upload_src(user=self.editor)
		self.mock_video_info.return_value = vid3
		res3 = self.upload_src(user=self.editor)

		self.mock_video_info.side_effect = [vid2, vid3]

		res4 = self.upload_src(
			is_reupload=True, has_original=True, work_id=res1.json(), user=self.editor
		)

		self.assertEqual(res4.json(), res1.json())
		self.assertEqual(MediaWork.objects.all().count(), 3)
		self.assertEqual(WorkSource.objects.filter(media=res1.json()).count(), 3)
		self.assertEqual(WorkSource.objects.filter(media=res2.json()).count(), 0)
		self.assertEqual(WorkSource.objects.filter(media=res3.json()).count(), 0)
