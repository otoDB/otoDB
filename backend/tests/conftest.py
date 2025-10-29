"""Shared pytest fixtures for all tests."""
import pytest
from ninja.testing import TestClient

from otodb.account.models import Account
from otodb.api.tag import tag_router
from otodb.api.work import work_router


# User fixtures
@pytest.fixture
def member(db):
	"""Create a member user for testing."""
	return Account.objects.create_user(
		'user', 'user@test.com', password='user_pass', level=Account.Levels.MEMBER
	)


@pytest.fixture
def editor(db):
	"""Create an editor user for testing."""
	return Account.objects.create_user(
		'editor', 'editor@test.com', password='editor_pass', level=Account.Levels.EDITOR
	)


# Client fixtures
@pytest.fixture
def work_client():
	"""Create a test client for the work router."""
	return TestClient(work_router)


@pytest.fixture
def tag_client():
	"""Create a test client for the tag router."""
	return TestClient(tag_router)
