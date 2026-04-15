"""Tests for PUT /api/post/close endpoint."""

import pytest

from otodb.account.models import Account
from otodb.api.post import post_router
from otodb.models.posts import Post, PostContent
from otodb.models.enums import PostCategory, LanguageTypes

from tests.conftest import AuthenticatedTestClient


@pytest.fixture
def owner(db):
	return Account.objects.create_user(
		'owner', 'owner@test.com', password='owner_pass', level=Account.Levels.OWNER
	)


@pytest.fixture
def post_client(member):
	return AuthenticatedTestClient(post_router, member)


@pytest.fixture
def owner_post_client(owner):
	return AuthenticatedTestClient(post_router, owner)


def make_post(member, category: PostCategory) -> Post:
	p = Post.objects.create(title='Test Post', added_by=member, category=category)
	PostContent.objects.create(post=p, lang=LanguageTypes.JAPANESE, page='content')
	return p


@pytest.mark.django_db
def test_close_post_as_owner(owner_post_client, owner):
	"""OWNER can close a BUG_REPORT post."""
	p = make_post(owner, PostCategory.BUG_REPORT)

	response = owner_post_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is not None


@pytest.mark.django_db
def test_close_post_feature_request(owner_post_client, owner):
	"""OWNER can close a FEATURE_REQUEST post."""
	p = make_post(owner, PostCategory.FEATURE_REQUEST)

	response = owner_post_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is not None


@pytest.mark.django_db
def test_close_post_forbidden_for_non_owner(post_client, member):
	"""Users below OWNER level receive 403."""
	p = make_post(member, PostCategory.BUG_REPORT)

	response = post_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_close_announcement_returns_400(owner_post_client, owner):
	"""ANNOUNCEMENT is not closable (is_closable=False) and returns 400."""
	p = make_post(owner, PostCategory.ANNOUNCEMENT)

	response = owner_post_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 400
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_close_nonexistent_post_returns_404(owner_post_client):
	"""Non-existent post_id returns 404."""
	response = owner_post_client.put('/close', json={'post_id': 99999})

	assert response.status_code == 404
