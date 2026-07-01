"""Tests for GET /api/thread/categories endpoint."""

from datetime import datetime, timezone

import pytest

from otodb.api.thread import thread_router
from otodb.models.enums import PostCategory
from otodb.models.posts import Thread, ThreadPost
from tests.conftest import AuthenticatedTestClient


@pytest.fixture
def thread_client(member):
	return AuthenticatedTestClient(thread_router, member)


def make_thread(member, *, closed: bool = False) -> Thread:
	t = Thread.objects.create(
		title='Test Thread',
		added_by=member,
		category=PostCategory.GENERAL,
		closed_at=datetime.now(tz=timezone.utc) if closed else None,
	)
	ThreadPost.objects.create(thread=t, num=1, user=member, body='content')
	return t


@pytest.mark.django_db
def test_categories_defaults_to_open_only(thread_client, member):
	"""By default, closed threads are excluded."""
	open_thread = make_thread(member, closed=False)
	make_thread(member, closed=True)

	response = thread_client.get('/categories')

	assert response.status_code == 200
	ids = [t['id'] for t in response.json()[str(PostCategory.GENERAL)]]
	assert ids == [str(open_thread.pk)]


@pytest.mark.django_db
def test_categories_is_open_false_returns_closed_only(thread_client, member):
	"""Passing is_open=false returns only closed threads."""
	make_thread(member, closed=False)
	closed_thread = make_thread(member, closed=True)

	response = thread_client.get('/categories?is_open=false')

	assert response.status_code == 200
	ids = [t['id'] for t in response.json()[str(PostCategory.GENERAL)]]
	assert ids == [str(closed_thread.pk)]
