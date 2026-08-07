"""Tests for GET /api/profile/activity (contribution heatmap data)."""

import datetime

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django_comments_xtd.models import XtdComment
from ninja.testing import TestClient

from otodb.api.profile import profile_router
from otodb.models import MediaWork, Revision
from otodb.models.enums import PostCategory
from otodb.models.posts import Thread, ThreadPost


@pytest.fixture
def profile_client():
	"""The endpoint is public, so no authenticated client is needed."""
	return TestClient(profile_router)


def utc_now() -> datetime.datetime:
	return datetime.datetime.now(datetime.UTC)


def days_ago(n: int) -> datetime.datetime:
	return utc_now() - datetime.timedelta(days=n)


def make_revision(user, when: datetime.datetime | None = None) -> Revision:
	"""Revision.date is auto_now_add, so backdating needs an UPDATE."""
	rev = Revision.objects.create(user=user, message='test')
	if when is not None:
		Revision.objects.filter(pk=rev.pk).update(date=when)
	return rev


def make_thread(user) -> Thread:
	return Thread.objects.create(
		title='Test Thread', added_by=user, category=PostCategory.GENERAL
	)


def make_post(
	thread: Thread,
	user,
	num: int,
	when: datetime.datetime,
	is_removed: bool = False,
) -> ThreadPost:
	return ThreadPost.objects.create(
		thread=thread,
		num=num,
		user=user,
		body='content',
		created_at=when,
		is_removed=is_removed,
	)


def make_comment(user, when: datetime.datetime, is_removed: bool = False) -> XtdComment:
	# object_pk need not resolve to a real row; only the user/date/flag matter,
	# and creating a real MediaWork would emit an extra Revision.
	return XtdComment.objects.create(
		content_type=ContentType.objects.get_for_model(MediaWork),
		object_pk='1',
		site_id=1,
		user=user,
		comment='comment',
		submit_date=when,
		is_removed=is_removed,
	)


def get_activity(client: TestClient, username: str):
	return client.get(f'/activity?username={username}')


@pytest.mark.django_db
def test_window_is_365_days_ending_today(profile_client, member):
	"""start/end span a 365-day window ending today (UTC)."""
	response = get_activity(profile_client, member.username)

	assert response.status_code == 200
	body = response.json()
	end = datetime.date.fromisoformat(body['end'])
	start = datetime.date.fromisoformat(body['start'])
	assert end == utc_now().date()
	assert (end - start).days == 364


@pytest.mark.django_db
def test_counts_aggregate_across_all_three_sources(profile_client, member):
	"""Revisions, thread posts and comments on the same day are summed."""
	when = days_ago(3)
	make_revision(member, when)
	make_revision(member, when)
	thread = make_thread(member)
	make_post(thread, member, 1, when)
	make_comment(member, when)

	body = get_activity(profile_client, member.username).json()

	assert body['days'] == [{'date': when.date().isoformat(), 'count': 4}]
	assert body['total'] == 4


@pytest.mark.django_db
def test_removed_posts_and_comments_are_excluded(profile_client, member):
	"""Soft-removed thread posts and comments do not count."""
	when = days_ago(2)
	thread = make_thread(member)
	make_post(thread, member, 1, when)
	make_post(thread, member, 2, when, is_removed=True)
	make_comment(member, when)
	make_comment(member, when, is_removed=True)

	body = get_activity(profile_client, member.username).json()

	assert body['days'] == [{'date': when.date().isoformat(), 'count': 2}]
	assert body['total'] == 2


@pytest.mark.django_db
def test_entries_outside_the_window_are_excluded(profile_client, member):
	"""Anything older than the 365-day window is dropped; the first day is kept."""
	inside = days_ago(364)
	make_revision(member, inside)
	make_revision(member, days_ago(365))
	make_revision(member, days_ago(400))
	thread = make_thread(member)
	make_post(thread, member, 1, days_ago(370))
	make_comment(member, days_ago(500))

	body = get_activity(profile_client, member.username).json()

	assert body['start'] == inside.date().isoformat()
	assert body['days'] == [{'date': inside.date().isoformat(), 'count': 1}]
	assert body['total'] == 1


@pytest.mark.django_db
def test_zero_count_days_are_omitted_and_days_are_sorted(profile_client, member):
	"""Only days with activity appear, ascending, and total sums them."""
	make_revision(member, days_ago(1))
	make_revision(member, days_ago(10))
	make_revision(member, days_ago(10))
	make_revision(member, days_ago(30))

	body = get_activity(profile_client, member.username).json()

	assert body['days'] == [
		{'date': days_ago(30).date().isoformat(), 'count': 1},
		{'date': days_ago(10).date().isoformat(), 'count': 2},
		{'date': days_ago(1).date().isoformat(), 'count': 1},
	]
	assert body['total'] == 4


@pytest.mark.django_db
def test_other_users_activity_is_not_counted(profile_client, member, editor):
	"""Only the requested user's own activity is reported."""
	when = days_ago(5)
	make_revision(member, when)
	make_revision(editor, when)
	make_revision(editor, when)

	body = get_activity(profile_client, member.username).json()

	assert body['total'] == 1


@pytest.mark.django_db
def test_username_lookup_is_case_insensitive(profile_client, member):
	make_revision(member, days_ago(1))

	response = get_activity(profile_client, member.username.upper())

	assert response.status_code == 200
	assert response.json()['total'] == 1


@pytest.mark.django_db
def test_unknown_username_returns_404(profile_client):
	response = get_activity(profile_client, 'nobody')

	assert response.status_code == 404


@pytest.mark.django_db
def test_response_is_cached_per_user(profile_client, member):
	"""The payload is cached, so new activity only shows up once it expires."""
	make_revision(member, days_ago(1))

	first = get_activity(profile_client, member.username).json()
	assert first['total'] == 1

	make_revision(member, days_ago(1))
	cached = get_activity(profile_client, member.username).json()
	assert cached == first

	cache.clear()
	fresh = get_activity(profile_client, member.username).json()
	assert fresh['total'] == 2


@pytest.mark.django_db
def test_cache_is_not_shared_between_users(profile_client, member, editor):
	make_revision(member, days_ago(1))
	make_revision(editor, days_ago(1))
	make_revision(editor, days_ago(1))

	assert get_activity(profile_client, member.username).json()['total'] == 1
	assert get_activity(profile_client, editor.username).json()['total'] == 2
