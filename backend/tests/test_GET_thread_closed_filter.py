"""Tests for the `closed` filter on GET /api/thread/category and GET /api/thread/search."""

import pytest

from otodb.api.thread import thread_router
from otodb.models.enums import PostCategory
from otodb.models.posts import Thread, ThreadPost
from tests.conftest import AuthenticatedTestClient


@pytest.fixture
def thread_client(member):
	return AuthenticatedTestClient(thread_router, member)


def make_thread(member, *, title='Test Thread', closed=False) -> Thread:
	t = Thread.objects.create(
		title=title,
		added_by=member,
		category=PostCategory.GENERAL,
	)
	ThreadPost.objects.create(thread=t, num=1, user=member, body='content')
	if closed:
		from datetime import datetime, timezone

		t.closed_at = datetime.now(tz=timezone.utc)
		t.save(update_fields=['closed_at'])
	return t


@pytest.mark.django_db
def test_category_default_returns_both_open_and_closed(thread_client, member):
	open_thread = make_thread(member, title='Open')
	closed_thread = make_thread(member, title='Closed', closed=True)

	response = thread_client.get(f'/category?category={PostCategory.GENERAL}')

	assert response.status_code == 200
	ids = {item['id'] for item in response.json()['items']}
	assert ids == {str(open_thread.pk), str(closed_thread.pk)}


@pytest.mark.django_db
def test_category_closed_0_returns_only_open(thread_client, member):
	open_thread = make_thread(member, title='Open')
	make_thread(member, title='Closed', closed=True)

	response = thread_client.get(f'/category?category={PostCategory.GENERAL}&closed=0')

	assert response.status_code == 200
	ids = {item['id'] for item in response.json()['items']}
	assert ids == {str(open_thread.pk)}


@pytest.mark.django_db
def test_category_closed_1_returns_only_closed(thread_client, member):
	make_thread(member, title='Open')
	closed_thread = make_thread(member, title='Closed', closed=True)

	response = thread_client.get(f'/category?category={PostCategory.GENERAL}&closed=1')

	assert response.status_code == 200
	ids = {item['id'] for item in response.json()['items']}
	assert ids == {str(closed_thread.pk)}


@pytest.mark.django_db
def test_search_default_returns_both_open_and_closed(thread_client, member):
	open_thread = make_thread(member, title='Findme Open')
	closed_thread = make_thread(member, title='Findme Closed', closed=True)

	response = thread_client.get('/search?query=Findme')

	assert response.status_code == 200
	ids = {item['id'] for item in response.json()['items']}
	assert ids == {str(open_thread.pk), str(closed_thread.pk)}


@pytest.mark.django_db
def test_search_closed_0_returns_only_open(thread_client, member):
	open_thread = make_thread(member, title='Findme Open')
	make_thread(member, title='Findme Closed', closed=True)

	response = thread_client.get('/search?query=Findme&closed=0')

	assert response.status_code == 200
	ids = {item['id'] for item in response.json()['items']}
	assert ids == {str(open_thread.pk)}


@pytest.mark.django_db
def test_search_closed_1_returns_only_closed(thread_client, member):
	make_thread(member, title='Findme Open')
	closed_thread = make_thread(member, title='Findme Closed', closed=True)

	response = thread_client.get('/search?query=Findme&closed=1')

	assert response.status_code == 200
	ids = {item['id'] for item in response.json()['items']}
	assert ids == {str(closed_thread.pk)}
