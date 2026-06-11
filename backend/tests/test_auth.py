"""Tests for authentication API endpoints."""

import pytest
from django.core import mail
from django.test import override_settings

from otodb.account.models import Account, Invitation
from otodb.api.auth import PASSWORD_RESET_EMAIL
from otodb.api.common import ApiError
from otodb.models import UserPreference
from otodb.models.enums import ErrorCode, LanguageTypes, Preferences


@pytest.mark.django_db
@override_settings(OTODB_TURNSTILE_SECRET_KEY=None)
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
@override_settings(OTODB_TURNSTILE_SECRET_KEY=None)
def test_password_reset_email_uses_language_preference(auth_client, member):
	"""Reset email is localized to the user's saved language preference."""
	UserPreference.objects.create(
		user=member, setting=Preferences.LANGUAGE, value=LanguageTypes.JAPANESE
	)

	response = auth_client.put('/reset_password', json={'email': 'user@test.com'})

	assert response.status_code == 200
	assert len(mail.outbox) == 1
	assert mail.outbox[0].subject == PASSWORD_RESET_EMAIL[LanguageTypes.JAPANESE][0]
	member.refresh_from_db()
	assert member.reset_token in mail.outbox[0].body


@pytest.mark.django_db
@override_settings(OTODB_TURNSTILE_SECRET_KEY=None)
def test_password_reset_email_na_language_falls_back_to_english(auth_client, member):
	"""A NOT_APPLICABLE language preference falls back to English instead of crashing."""
	UserPreference.objects.create(
		user=member, setting=Preferences.LANGUAGE, value=LanguageTypes.NOT_APPLICABLE
	)

	response = auth_client.put('/reset_password', json={'email': 'user@test.com'})

	assert response.status_code == 200
	assert len(mail.outbox) == 1
	assert mail.outbox[0].subject == PASSWORD_RESET_EMAIL[LanguageTypes.ENGLISH][0]


@pytest.mark.django_db
@override_settings(OTODB_TURNSTILE_SECRET_KEY=None)
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
@override_settings(OTODB_TURNSTILE_SECRET_KEY=None)
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
@override_settings(OTODB_INVITE_REQUIRED=False, OTODB_TURNSTILE_SECRET_KEY=None)
def test_register_open_registration_succeeds(auth_client, monkeypatch):
	"""Open registration: invite is optional and new users default to MEMBER."""
	monkeypatch.setattr('otodb.api.auth.login', lambda *a, **k: None)
	response = auth_client.post(
		'/register',
		json={
			'username': 'newuser',
			'password': 'a-strong-password-123',
			'email': 'newuser@test.com',
		},
	)
	assert response.status_code == 200
	user = Account.objects.get(username='newuser')
	assert user.level == Account.Levels.MEMBER


@pytest.mark.django_db
@override_settings(OTODB_INVITE_REQUIRED=False, OTODB_TURNSTILE_SECRET_KEY=None)
@pytest.mark.parametrize('email', ['notanemail', 'a@', '@b.com', 'user @ example.com'])
def test_register_invalid_email_fails(auth_client, monkeypatch, email):
	"""Registration rejects malformed email addresses and creates no account."""
	monkeypatch.setattr('otodb.api.auth.login', lambda *a, **k: None)
	with pytest.raises(ApiError) as exc_info:
		auth_client.post(
			'/register',
			json={
				'username': 'bademail',
				'password': 'a-strong-password-123',
				'email': email,
			},
		)
	assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
	assert not Account.objects.filter(username='bademail').exists()


@pytest.mark.django_db
@override_settings(OTODB_INVITE_REQUIRED=True, OTODB_TURNSTILE_SECRET_KEY=None)
def test_register_invite_required_with_valid_invite(auth_client, editor, monkeypatch):
	"""Invite-required mode: a valid invite grants its level to the new user."""
	monkeypatch.setattr('otodb.api.auth.login', lambda *a, **k: None)
	invite = Invitation.objects.create(
		secret='valid-invite-secret',
		level=Account.Levels.EDITOR,
		created_by=editor,
	)
	response = auth_client.post(
		'/register',
		json={
			'username': 'invited',
			'password': 'a-strong-password-123',
			'email': 'invited@test.com',
			'invite': 'valid-invite-secret',
		},
	)
	assert response.status_code == 200
	user = Account.objects.get(username='invited')
	assert user.level == Account.Levels.EDITOR
	invite.refresh_from_db()
	assert invite.used_by_id == user.id
	assert invite.used_at is not None


@pytest.mark.django_db
@override_settings(OTODB_INVITE_REQUIRED=True, OTODB_TURNSTILE_SECRET_KEY=None)
def test_register_invite_required_without_invite_fails(auth_client):
	"""Invite-required mode rejects registrations without an invite."""
	with pytest.raises(ApiError) as exc_info:
		auth_client.post(
			'/register',
			json={
				'username': 'noinvite',
				'password': 'a-strong-password-123',
				'email': 'noinvite@test.com',
			},
		)
	assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
	assert not Account.objects.filter(username='noinvite').exists()


@pytest.mark.django_db
@override_settings(
	OTODB_INVITE_REQUIRED=False, OTODB_TURNSTILE_SECRET_KEY='test-secret'
)
def test_register_missing_turnstile_token_fails(auth_client):
	"""When Turnstile is configured, registration without a token is rejected."""
	with pytest.raises(ApiError) as exc_info:
		auth_client.post(
			'/register',
			json={
				'username': 'no-captcha',
				'password': 'a-strong-password-123',
				'email': 'no-captcha@test.com',
			},
		)
	assert exc_info.value.code == ErrorCode.CAPTCHA_FAILED
	assert not Account.objects.filter(username='no-captcha').exists()


@pytest.mark.django_db
@override_settings(
	OTODB_INVITE_REQUIRED=False, OTODB_TURNSTILE_SECRET_KEY='test-secret'
)
def test_register_with_valid_turnstile_token_succeeds(auth_client, monkeypatch):
	"""When Turnstile is configured and the token verifies, registration succeeds."""
	monkeypatch.setattr('otodb.api.auth.verify_turnstile', lambda *a, **k: None)
	monkeypatch.setattr('otodb.api.auth.login', lambda *a, **k: None)
	response = auth_client.post(
		'/register',
		json={
			'username': 'captcha-ok',
			'password': 'a-strong-password-123',
			'email': 'captcha-ok@test.com',
			'turnstile_token': 'verified-token',
		},
	)
	assert response.status_code == 200
	assert Account.objects.filter(username='captcha-ok').exists()


@pytest.mark.django_db
@override_settings(OTODB_TURNSTILE_SECRET_KEY='test-secret')
def test_login_missing_turnstile_token_fails(auth_client, member):
	"""When Turnstile is configured, login without a token is rejected."""
	with pytest.raises(ApiError) as exc_info:
		auth_client.post('/login', json={'username': 'user', 'password': 'user_pass'})
	assert exc_info.value.code == ErrorCode.CAPTCHA_FAILED


@pytest.mark.django_db
@override_settings(OTODB_TURNSTILE_SECRET_KEY='test-secret')
def test_password_reset_request_missing_turnstile_token_fails(auth_client, member):
	"""When Turnstile is configured, password-reset request without a token is rejected."""
	with pytest.raises(ApiError) as exc_info:
		auth_client.put('/reset_password', json={'email': 'user@test.com'})
	assert exc_info.value.code == ErrorCode.CAPTCHA_FAILED
	assert len(mail.outbox) == 0


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
