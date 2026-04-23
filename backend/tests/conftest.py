"""Shared pytest fixtures for all tests."""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.test import RequestFactory
from ninja.testing import TestClient

from otodb.account.models import Account
from otodb.api.auth import auth_router
from otodb.api.source import source_router
from otodb.api.tag import tag_router
from otodb.api.work import work_router
from otodb.models import MediaWork, Revision, RevisionChange


@pytest.fixture(autouse=True)
def clear_cache():
	cache.clear()
	yield
	cache.clear()


class AuthenticatedTestClient(TestClient):
	"""TestClient that automatically uses a real user for all requests."""

	def __init__(self, router, user):
		super().__init__(router)
		self.test_user = user

	def _build_request(self, method, path, data, request_params):
		"""Override to set real user on request object."""
		# If no user was explicitly provided, use our default test user
		if 'user' not in request_params:
			request_params['user'] = self.test_user
		return super()._build_request(method, path, data, request_params)


# Request cache fixture
@pytest.fixture(autouse=True)
def enable_request_cache(db, member):
	"""Enable request cache for all tests to support revision tracking."""
	from django_request_cache.middleware import RequestCache
	from django_userforeignkey import request as ufk_request

	# Create a fake request with cache attribute using the actual RequestCache
	factory = RequestFactory()
	request = factory.get('/')
	request.cache = RequestCache()
	request.user = member  # Set a real user for revision tracking

	# Initialize cache keys for revision tracking
	request.cache.add('rev', {})
	request.cache.add('rev_del', [])
	request.cache.add('rev_msg', '')

	# Set it as the current request
	ufk_request.set_current_request(request)

	yield

	# Clean up
	ufk_request.set_current_request(None)


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
def work_client(member):
	"""Create a test client for the work router."""
	return AuthenticatedTestClient(work_router, member)


@pytest.fixture
def tag_client(member):
	"""Create a test client for the tag router."""
	return AuthenticatedTestClient(tag_router, member)


@pytest.fixture
def source_client(member):
	"""Create a test client for the source router."""
	return AuthenticatedTestClient(source_router, member)


@pytest.fixture
def auth_client(member):
	"""Create a test client for the auth router."""
	return AuthenticatedTestClient(auth_router, member)


# Revision tracking fixtures
@pytest.fixture
def test_work(db, member):
	"""Create a test MediaWork for revision testing."""
	return MediaWork.objects.create(
		title='Test Work', description='Test Description', rating=0
	)


@pytest.fixture
def test_revision(db, member):
	"""Create a test Revision."""
	return Revision.objects.create(user=member, message='Test revision')


@pytest.fixture
def test_revision_change(db, test_revision, test_work):
	"""Create a test RevisionChange for a MediaWork."""
	content_type = ContentType.objects.get_for_model(MediaWork)
	return RevisionChange.objects.create(
		rev=test_revision,
		target_type=content_type,
		target_id=test_work.pk,
		target_column='title',
		target_value='Test Work',
	)
