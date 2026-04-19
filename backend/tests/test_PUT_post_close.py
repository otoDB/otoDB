"""Tests for PUT /api/post/close endpoint."""

import pytest

from otodb.account.models import Account
from otodb.api.post import post_router
from otodb.models.posts import Post, PostContent
from otodb.models.enums import PostCategory, LanguageTypes

from tests.conftest import AuthenticatedTestClient


@pytest.fixture
def admin(db):
	return Account.objects.create_user(
		'admin', 'admin@test.com', password='admin_pass', level=Account.Levels.ADMIN
	)


@pytest.fixture
def post_client(member):
	return AuthenticatedTestClient(post_router, member)


@pytest.fixture
def admin_post_client(admin):
	return AuthenticatedTestClient(post_router, admin)


def make_post(member) -> Post:
	p = Post.objects.create(
		title='Test Post', added_by=member, category=PostCategory.GENERAL
	)
	PostContent.objects.create(post=p, lang=LanguageTypes.JAPANESE, page='content')
	return p


@pytest.mark.django_db
def test_close_post_as_admin(admin_post_client, admin):
	"""ADMIN can close any post."""
	p = make_post(admin)

	response = admin_post_client.put(f'/close?post_id={p.pk}')

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is not None


@pytest.fixture
def other_member(db):
	return Account.objects.create_user(
		'other', 'other@test.com', password='other_pass', level=Account.Levels.MEMBER
	)


@pytest.mark.django_db
def test_close_post_as_author(post_client, member):
	"""Post author cannot close their own post."""
	p = make_post(member)

	response = post_client.put(f'/close?post_id={p.pk}')

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_close_post_forbidden_for_non_admin_non_author(other_member, member):
	"""Users who are neither ADMIN nor the post author receive 403."""
	p = make_post(member)
	other_client = AuthenticatedTestClient(post_router, other_member)

	response = other_client.put(f'/close?post_id={p.pk}')

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at is None


def make_closed_post(member) -> Post:
	from datetime import datetime, timezone
	p = make_post(member)
	p.closed_at = datetime.now(tz=timezone.utc)
	p.save()
	return p


@pytest.mark.django_db
def test_unclose_post_as_admin(admin_post_client, admin):
	"""ADMIN can unclose a closed post."""
	p = make_closed_post(admin)
	assert p.closed_at is not None

	response = admin_post_client.put(f'/close?post_id={p.pk}')

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_unclose_post_as_author(post_client, member):
	"""Post author can unclose their own closed post."""
	p = make_closed_post(member)
	assert p.closed_at is not None

	response = post_client.put(f'/close?post_id={p.pk}')

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_unclose_post_forbidden_for_non_admin_non_author(other_member, member):
	"""Users who are neither ADMIN nor the post author receive 403."""
	p = make_closed_post(member)
	original_closed_at = p.closed_at
	other_client = AuthenticatedTestClient(post_router, other_member)

	response = other_client.put(f'/close?post_id={p.pk}')

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at == original_closed_at
