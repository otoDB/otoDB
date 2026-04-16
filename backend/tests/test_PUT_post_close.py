"""Tests for PUT /api/post/close endpoint."""

import pytest

from otodb.account.models import Account
from otodb.api.post import post_router
from otodb.models.posts import Post, PostContent
from otodb.models.enums import PostCategory, LanguageTypes

from tests.conftest import AuthenticatedTestClient


ALL_CATEGORIES = [
	PostCategory.ANNOUNCEMENT,
	PostCategory.FEATURE_REQUEST,
	PostCategory.BUG_REPORT,
	PostCategory.GARDENING,
	PostCategory.GENERAL,
]


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
@pytest.mark.parametrize('category', ALL_CATEGORIES)
def test_close_post_as_owner(owner_post_client, owner, category):
	"""OWNER can close any category post."""
	p = make_post(owner, category)

	response = owner_post_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is not None


@pytest.fixture
def other_member(db):
	return Account.objects.create_user(
		'other', 'other@test.com', password='other_pass', level=Account.Levels.MEMBER
	)


@pytest.mark.django_db
@pytest.mark.parametrize('category', ALL_CATEGORIES)
def test_close_post_as_author(post_client, member, category):
	"""Post author can close their own post for any category."""
	p = make_post(member, category)

	response = post_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is not None


@pytest.mark.django_db
@pytest.mark.parametrize('category', ALL_CATEGORIES)
def test_close_post_forbidden_for_non_owner_non_author(other_member, member, category):
	"""Users who are neither OWNER nor the post author receive 403."""
	p = make_post(member, category)
	other_client = AuthenticatedTestClient(post_router, other_member)

	response = other_client.put('/close', json={'post_id': p.pk})

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at is None


'''
TODO(sno2wman): I think there should also be a error test for fetching a non-existent Post.
@pytest.mark.django_db
def test_close_nonexistent_post_returns_404(owner_post_client):
    """Non-existent post_id returns 404."""
    response = owner_post_client.put('/close', json={'post_id': 99999})

    assert response.status_code == 404
'''
