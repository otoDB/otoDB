from django.test import TestCase
from ninja.testing import TestClient
from otodb.api.work import work_router
from otodb.account.models import Account
from otodb.models import WorkSource, MediaWork
from urllib.parse import urlencode
from unittest.mock import patch
from otodb.common import process_video_info
from pathlib import Path
import json
import random
import string
import time


def random_str(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def get_video_infos_mock():
    json_path = Path(__file__).parent / "mocks" / "video_info.json"
    with json_path.open() as f:
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
    @classmethod
    def setUpTestData(self):
        self.v_info = get_video_infos_mock()
        
    def setUp(self):
        self.patcher = patch('otodb.models.work_source.video_info')
        self.mock_video_info = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        self.mock_video_info.return_value = fuzz_video_infos(self.v_info)

        self.member = Account.objects.create_user(
            "user", "user@test.com", password="user_pass", level=Account.Levels.MEMBER
        )
        self.editor = Account.objects.create_user(
            "editor", "editor@test.com", password="editor_pass", level=Account.Levels.EDITOR
        )
        self.client = TestClient(work_router)

    def upload_src(self, url: str, is_reupload = False, rating = 0, work_id: int | None = None, original_url: str | None = None, user = None):
        payload = {
            "url":url,
            "is_reupload": is_reupload,
        }
        if (work_id is not None): payload['work_id'] = work_id
        if (original_url is not None): payload['original_url'] = original_url

        return self.client.post(
            '/source?' + urlencode(payload),
            content_type="application/x-www-form-urlencoded", 
            user=user
        )

    def test_add_single_work_as_member(self):
        res = self.upload_src("https://youtu.be/fakeUrl", user=self.member)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), None)
        self.assertEqual(MediaWork.objects.all().count(), 0)
        self.assertEqual(WorkSource.objects.all().count(), 1)

    def test_add_single_work_as_editor(self):
        res = self.upload_src("https://youtu.be/fakeUrl", user=self.editor)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), 1)
        self.assertEqual(MediaWork.objects.all().count(), 1)
        self.assertEqual(WorkSource.objects.all().count(), 1)

    def test_add_dual_work_as_editor(self):

        vid1 = fuzz_video_infos(self.v_info)
        vid2 = fuzz_video_infos(self.v_info)
        self.mock_video_info.side_effect = [vid1, vid2]

        res = self.upload_src(
            "https://youtu.be/fakeUrl", user=self.editor, 
            is_reupload=True, original_url="https://youtu.be/fakeUrl"
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), 1)
        self.assertEqual(MediaWork.objects.all().count(), 1)
        self.assertEqual(WorkSource.objects.all().count(), 2)

    def test_add_to_known_existing_work_as_member(self):
        res = self.upload_src("https://youtu.be/fakeUrl", user=self.editor)
        self.assertEqual(res.json(), 1)
        self.assertEqual(MediaWork.objects.all().count(), 1)
        self.assertEqual(WorkSource.objects.all().count(), 1)

        self.mock_video_info.return_value = fuzz_video_infos(self.v_info)

        res = self.upload_src("https://youtu.be/fakeUrl", work_id=1, user=self.member)
        self.assertEqual(res.json(), 1)
        self.assertEqual(MediaWork.objects.all().count(), 1)
        self.assertEqual(WorkSource.objects.all().count(), 2)

    def test_add_both_to_known_existing_work_as_member(self):
        res = self.upload_src("https://youtu.be/fakeUrl", user=self.editor)
        self.assertEqual(res.json(), 1)
        self.assertEqual(MediaWork.objects.all().count(), 1)
        self.assertEqual(WorkSource.objects.all().count(), 1)

        vid1 = fuzz_video_infos(self.v_info)
        vid2 = fuzz_video_infos(self.v_info)
        self.mock_video_info.side_effect = [vid1, vid2]

        res = self.upload_src(
            "https://youtu.be/fakeUrl", work_id=1, is_reupload=True, 
            original_url="https://youtu.be/fakeUrl", user=self.member
        )
        self.assertEqual(res.json(), 1)
        self.assertEqual(MediaWork.objects.all().count(), 1)
        self.assertEqual(WorkSource.objects.all().count(), 3)