"""Tests for PUT /api/post/unclose endpoint."""

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


def make_closed_post(member, category: PostCategory) -> Post:
	from datetime import datetime, timezone

	p = Post.objects.create(
		title='Test Post',
		added_by=member,
		category=category,
		closed_at=datetime.now(tz=timezone.utc),
	)
	PostContent.objects.create(post=p, lang=LanguageTypes.JAPANESE, page='content')
	return p


@pytest.mark.django_db
@pytest.mark.parametrize('category', ALL_CATEGORIES)
def test_unclose_post_as_owner(owner_post_client, owner, category):
	"""OWNER can unclose a closed post for any category."""
	p = make_closed_post(owner, category)
	assert p.closed_at is not None

	response = owner_post_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.fixture
def other_member(db):
	return Account.objects.create_user(
		'other', 'other@test.com', password='other_pass', level=Account.Levels.MEMBER
	)


@pytest.mark.django_db
@pytest.mark.parametrize('category', ALL_CATEGORIES)
def test_unclose_post_as_author(post_client, member, category):
	"""Post author can unclose their own closed post for any category."""
	p = make_closed_post(member, category)
	assert p.closed_at is not None

	response = post_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
@pytest.mark.parametrize('category', ALL_CATEGORIES)
def test_unclose_post_forbidden_for_non_owner_non_author(
	other_member, member, category
):
	"""Users who are neither OWNER nor the post author receive 403."""
	p = make_closed_post(member, category)
	original_closed_at = p.closed_at
	other_client = AuthenticatedTestClient(post_router, other_member)

	response = other_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at == original_closed_at
