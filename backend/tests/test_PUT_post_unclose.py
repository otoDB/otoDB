"""Tests for PUT /api/post/unclose endpoint."""

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
def test_unclose_post_as_owner(owner_post_client, owner):
	"""OWNER can unclose a closed BUG_REPORT post."""
	p = make_closed_post(owner, PostCategory.BUG_REPORT)
	assert p.closed_at is not None

	response = owner_post_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_unclose_post_feature_request(owner_post_client, owner):
	"""OWNER can unclose a closed FEATURE_REQUEST post."""
	p = make_closed_post(owner, PostCategory.FEATURE_REQUEST)

	response = owner_post_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 200
	p.refresh_from_db()
	assert p.closed_at is None


@pytest.mark.django_db
def test_unclose_post_forbidden_for_non_owner(post_client, member):
	"""Users below OWNER level receive 403."""
	p = make_closed_post(member, PostCategory.BUG_REPORT)
	original_closed_at = p.closed_at

	response = post_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at == original_closed_at


@pytest.mark.django_db
def test_unclose_announcement_returns_403(owner_post_client, owner):
	"""ANNOUNCEMENT is not closable (is_closable=False) and returns 403."""
	p = make_closed_post(owner, PostCategory.ANNOUNCEMENT)

	response = owner_post_client.put('/unclose', json={'post_id': p.pk})

	assert response.status_code == 403
	p.refresh_from_db()
	assert p.closed_at is not None
