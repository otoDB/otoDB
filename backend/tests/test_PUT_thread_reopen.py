"""Tests for PUT /api/thread/reopen endpoint."""

from datetime import UTC, datetime

import pytest

from otodb.account.models import Account
from otodb.api.thread import thread_router
from otodb.models.enums import PostCategory
from otodb.models.posts import Thread, ThreadPost
from tests.conftest import AuthenticatedTestClient


@pytest.fixture
def admin(db):
	return Account.objects.create_user(
		'admin', 'admin@test.com', password='admin_pass', level=Account.Levels.ADMIN
	)


@pytest.fixture
def thread_client(member):
	return AuthenticatedTestClient(thread_router, member)


@pytest.fixture
def admin_thread_client(admin):
	return AuthenticatedTestClient(thread_router, admin)


@pytest.fixture
def other_member(db):
	return Account.objects.create_user(
		'other', 'other@test.com', password='other_pass', level=Account.Levels.MEMBER
	)


def make_closed_thread(member) -> Thread:
	t = Thread.objects.create(
		title='Test Thread',
		added_by=member,
		category=PostCategory.GENERAL,
		closed_at=datetime.now(tz=UTC),
	)
	ThreadPost.objects.create(thread=t, num=1, user=member, body='content')
	return t


@pytest.mark.django_db
def test_reopen_thread_as_admin(admin_thread_client, admin):
	"""ADMIN can reopen a closed thread."""
	t = make_closed_thread(admin)
	assert t.closed_at is not None

	response = admin_thread_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 200
	t.refresh_from_db()
	assert t.closed_at is None


@pytest.mark.django_db
def test_reopen_thread_as_author(thread_client, member):
	"""Thread author can reopen their own closed thread."""
	t = make_closed_thread(member)
	assert t.closed_at is not None

	response = thread_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 200
	t.refresh_from_db()
	assert t.closed_at is None


@pytest.mark.django_db
def test_reopen_thread_forbidden_for_non_admin_non_author(other_member, member):
	"""Users who are neither ADMIN nor the thread author receive 403."""
	t = make_closed_thread(member)
	original_closed_at = t.closed_at
	other_client = AuthenticatedTestClient(thread_router, other_member)

	response = other_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 403
	t.refresh_from_db()
	assert t.closed_at == original_closed_at


@pytest.mark.django_db
def test_reopen_forbidden_for_author_when_op_edited_by_mod(
	thread_client, member, admin
):
	"""Author cannot reopen once a mod has edited the OP (mod intervention)."""
	t = make_closed_thread(member)
	op = t.posts.get(num=1)
	op.edited_by = admin
	op.edited_at = datetime.now(tz=UTC)
	op.save(update_fields=['edited_by', 'edited_at'])
	original_closed_at = t.closed_at

	response = thread_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 403
	t.refresh_from_db()
	assert t.closed_at == original_closed_at


@pytest.mark.django_db
def test_reopen_allowed_for_author_when_op_edited_by_self(thread_client, member):
	"""An author editing their own OP does not lock reopening."""
	t = make_closed_thread(member)
	op = t.posts.get(num=1)
	op.edited_by = member
	op.edited_at = datetime.now(tz=UTC)
	op.save(update_fields=['edited_by', 'edited_at'])

	response = thread_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 200
	t.refresh_from_db()
	assert t.closed_at is None


@pytest.mark.django_db
def test_reopen_allowed_for_mod_when_op_edited_by_mod(
	admin_thread_client, member, admin
):
	"""A mod can still reopen even after the OP was edited by a mod."""
	t = make_closed_thread(member)
	op = t.posts.get(num=1)
	op.edited_by = admin
	op.edited_at = datetime.now(tz=UTC)
	op.save(update_fields=['edited_by', 'edited_at'])

	response = admin_thread_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 200
	t.refresh_from_db()
	assert t.closed_at is None


@pytest.mark.django_db
def test_reopen_already_open_thread(admin_thread_client, admin):
	"""Reopening a thread that is not closed is a no-op."""
	t = Thread.objects.create(
		title='Test Thread',
		added_by=admin,
		category=PostCategory.GENERAL,
	)
	ThreadPost.objects.create(thread=t, num=1, user=admin, body='content')

	response = admin_thread_client.put(f'/reopen?thread_id={t.pk}')

	assert response.status_code == 200
	t.refresh_from_db()
	assert t.closed_at is None
