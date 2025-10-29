"""Tests for authentication API endpoints."""

from urllib.parse import urlencode

import pytest
from django.core import mail
from ninja.testing import TestClient

from otodb.account.models import Account
from otodb.api.auth import auth_router


@pytest.fixture
def auth_client():
	"""Create a test client for the auth router."""
	return TestClient(auth_router)


@pytest.mark.django_db
def test_password_reset_email_sends_successfully(auth_client):
	"""Test that password reset email is sent with correct format.
	"""
	# Create a test user
	user = Account.objects.create_user(
		username='testuser',
		email='test@example.com',
		password='old_password'
	)

	# Request password reset
	response = auth_client.put('/reset_password?' + urlencode({'email': 'test@example.com'}))

	# Should return success (200) even if email doesn't exist (security best practice)
	assert response.status_code == 200

	# Verify email was sent
	assert len(mail.outbox) == 1

	# Verify email has correct recipient
	assert mail.outbox[0].to == ['test@example.com']

	# Verify email has subject
	assert isinstance(mail.outbox[0].subject, str)
	assert len(mail.outbox[0].subject) > 0
	assert '[otodb.net]' in mail.outbox[0].subject

	# Verify email body is a string
	assert isinstance(mail.outbox[0].body, str)

	# Verify email body contains expected content
	assert 'testuser' in mail.outbox[0].body  # Username should be in body

	# Verify reset token was generated and is in the email
	user.refresh_from_db()
	assert user.reset_token is not None
	assert len(user.reset_token) == 120  # Token should be 120 chars
	assert user.reset_token in mail.outbox[0].body  # Token should be in email body

	# Verify the reset URL is properly formatted in the email
	assert f'https://otodb.net/reset_password?token={user.reset_token}' in mail.outbox[0].body


@pytest.mark.django_db
def test_password_reset_email_nonexistent_user(auth_client):
	"""Test that password reset doesn't reveal if user exists (security best practice)."""
	# Request password reset for non-existent email
	response = auth_client.put('/reset_password?' + urlencode({'email': 'nonexistent@example.com'}))

	# Should still return success to prevent user enumeration
	assert response.status_code == 200

	# But no email should be sent
	assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_password_reset_token_uniqueness(auth_client):
	"""Test that each password reset generates a unique token."""
	user = Account.objects.create_user(
		username='testuser',
		email='test@example.com',
		password='password'
	)

	# Request first reset
	auth_client.put('/reset_password?' + urlencode({'email': 'test@example.com'}))
	user.refresh_from_db()
	first_token = user.reset_token

	# Clear mail outbox
	mail.outbox.clear()

	# Request second reset
	auth_client.put('/reset_password?' + urlencode({'email': 'test@example.com'}))
	user.refresh_from_db()
	second_token = user.reset_token

	# Tokens should be different
	assert first_token != second_token
	assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_logout_does_not_crash_on_session_deletion(auth_client):
	"""Test that deleting a session (logout) doesn't crash the pre_delete signal.

	This test prevents regression where the pre_delete signal handler tried to
	query UserRequest objects for Session instances, causing a crash on logout.

	Bug was fixed in commit b022b83.
	"""
	from django.contrib.sessions.models import Session
	from django.contrib.auth import get_user_model

	User = get_user_model()

	# Create a user and session
	user = User.objects.create_user(
		username='testuser',
		email='test@example.com',
		password='password'
	)

	# Create a session (simulating login)
	session = Session.objects.create(
		session_key='test_session_key_12345',
		session_data='encoded_session_data',
		expire_date='2030-01-01'
	)

	# Delete the session (simulating logout)
	# This should NOT crash due to pre_delete signal
	try:
		session.delete()
		# If we reach here, the test passed
		assert True
	except Exception as e:
		# If an exception is raised, the test should fail
		pytest.fail(f'Session deletion (logout) crashed with error: {e}')
