"""Tests for username validation in AccountManager.create_user."""

import pytest
from django.db import IntegrityError
from django.test import override_settings

from otodb.account.models import Account
from otodb.api.common import ApiError
from otodb.models.enums import ErrorCode

EMAIL = 'new-account@test.com'
VALID_USERNAMES = [
	'alice',
	'bob_99',
	'jane.doe',
	'x-ray',
	'_alice',
	'alice.',
	'a__b',
	'a~b',
	'a',  # single character
	'x' * 32,  # maximum length
	'café',  # accented Latin
	'Müller',
	'محمد',  # Arabic
	'Дмитрий',  # Cyrillic
	'Ελλάς',  # Greek
	'さくら',  # Hiragana
	'ナルト',  # Katakana
	'東京',  # Han
	'김철수',  # Hangul
	'🍕pizza',  # Emoji
]
INVALID_USERNAMES = [
	'x' * 33,  # too long
	'a@b',  # "@"
	'a/b',  # forward slash
	'a\\b',  # backslash
	'a?b',  # URL query
	'a#b',  # URL fragment
	'a&b',
	'a=b',
	'a:b',
	'a%25b',  # percent-encoding
	'a<b',  # HTML
	'a>b',  # HTML
	'a"b',  # HTML
	'a{b',  # Markdown / search syntax
	'a}b',  # Markdown / search syntax
	'a|b',  # Markdown / search syntax
	'a^b',  # Markdown / search syntax
	"a'b",  # apostrophe / markup
	'a b',  # ASCII whitespace
	'a　b',  # ideographic space
	'a\tb',  # tab
	'a\x00b',  # NUL
	'a\x1bb',  # ESC
	'a​b',  # zero-width space
	'a‮b',  # right-to-left override
]


@pytest.mark.django_db
@pytest.mark.parametrize('username', VALID_USERNAMES)
def test_create_user_accepts_valid_usernames(username):
	user = Account.objects.create_user(username, EMAIL, password='pw')
	assert user.username == username


@pytest.mark.django_db
@pytest.mark.parametrize('username', INVALID_USERNAMES)
def test_create_user_rejects_invalid_usernames(username):
	with pytest.raises(ValueError):
		Account.objects.create_user(username, EMAIL, password='pw')
	# Query by the (ASCII) email: a rejected username may contain a NUL byte,
	# which PostgreSQL cannot store or query.
	assert not Account.objects.filter(email=EMAIL).exists()


@pytest.mark.django_db
def test_create_user_normalizes_fullwidth_characters_before_validating():
	# Full-width "ａ＠ｂ" NFKC-normalizes to "a@b", so the "@" is still rejected
	with pytest.raises(ValueError, match='may not contain'):
		Account.objects.create_user('ａ＠ｂ', EMAIL, password='pw')


@pytest.mark.django_db
def test_create_user_normalizes_before_uniqueness_check():
	Account.objects.create_user('file', 'file1@test.com', password='pw')
	with pytest.raises(IntegrityError):
		Account.objects.create_user('ﬁle', 'file2@test.com', password='pw')


@pytest.mark.django_db
def test_create_user_uniqueness_is_case_insensitive():
	Account.objects.create_user('Alice', 'alice1@test.com', password='pw')
	with pytest.raises(IntegrityError):
		Account.objects.create_user('alice', 'alice2@test.com', password='pw')


@pytest.mark.django_db
@override_settings(OTODB_INVITE_REQUIRED=False, OTODB_TURNSTILE_SECRET_KEY=None)
def test_register_rejects_invalid_username(auth_client, monkeypatch):
	"""Registration surfaces an invalid username as a VALIDATION_ERROR."""
	monkeypatch.setattr('otodb.api.auth.login', lambda *a, **k: None)
	with pytest.raises(ApiError) as exc_info:
		auth_client.post(
			'/register',
			json={
				'username': 'bad@name',
				'password': 'a-strong-password-123',
				'email': 'bad-name@test.com',
			},
		)
	assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
	assert not Account.objects.filter(username='bad@name').exists()
