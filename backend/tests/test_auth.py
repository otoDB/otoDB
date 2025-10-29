"""Tests for authentication API endpoints."""

import pytest
from django.core import mail


@pytest.mark.django_db
def test_password_reset_email_sends_successfully(auth_client, member):
	"""Test that password reset email is sent with correct format."""
	# Request password reset using member fixture
	response = auth_client.put('/reset_password', json={'email': 'user@test.com'})

	# Should return success (200) even if email doesn't exist (security best practice)
	assert response.status_code == 200

	# Verify email was sent
	assert len(mail.outbox) == 1

	# Verify email has correct recipient
	assert mail.outbox[0].to == ['user@test.com']

	# Verify email has subject
	assert isinstance(mail.outbox[0].subject, str)
	assert len(mail.outbox[0].subject) > 0
	assert '[otodb.net]' in mail.outbox[0].subject

	# Verify email body is a string
	assert isinstance(mail.outbox[0].body, str)

	# Verify email body contains expected content
	assert 'user' in mail.outbox[0].body  # Username should be in body

	# Verify reset token was generated and is in the email
	member.refresh_from_db()
	assert member.reset_token is not None
	assert len(member.reset_token) == 120  # Token should be 120 chars
	assert member.reset_token in mail.outbox[0].body  # Token should be in email body

	# Verify the reset URL is properly formatted in the email
	assert (
		f'https://otodb.net/reset_password?token={member.reset_token}'
		in mail.outbox[0].body
	)


@pytest.mark.django_db
def test_password_reset_email_nonexistent_user(auth_client):
	"""Test that password reset doesn't reveal if user exists (security best practice)."""
	# Request password reset for non-existent email
	response = auth_client.put(
		'/reset_password', json={'email': 'nonexistent@example.com'}
	)

	# Should still return success to prevent user enumeration
	assert response.status_code == 200

	# But no email should be sent
	assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_password_reset_token_uniqueness(auth_client, editor):
	"""Test that each password reset generates a unique token."""
	# Request first reset using editor fixture
	auth_client.put('/reset_password', json={'email': 'editor@test.com'})
	editor.refresh_from_db()
	first_token = editor.reset_token

	# Clear mail outbox
	mail.outbox.clear()

	# Request second reset
	auth_client.put('/reset_password', json={'email': 'editor@test.com'})
	editor.refresh_from_db()
	second_token = editor.reset_token

	# Tokens should be different
	assert first_token != second_token
	assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_logout_does_not_crash_on_session_deletion(member):
	"""Test that deleting a session (logout) doesn't crash the pre_delete signal.

	This test prevents regression where the pre_delete signal handler tried to
	query UserRequest objects for Session instances, causing a crash on logout.

	Bug was fixed in commit b022b83.
	"""
	from django.contrib.sessions.models import Session

	# Create a session (simulating login for member user)
	session = Session.objects.create(
		session_key='test_session_key_12345',
		session_data='encoded_session_data',
		expire_date='2030-01-01',
	)

	# Delete the session (simulating logout)
	# This should NOT crash due to pre_delete signal
	session.delete()
	# If we reach here without exception, the test passed
