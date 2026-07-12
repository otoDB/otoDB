"""Tests for the Django-session auth middleware on the Litestar app.

The database is faked, but the session payloads are produced with Django's own
signing machinery and the auth hash with the real Account model, so the
compatibility claims are checked against Django itself rather than a
re-implementation.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from django.conf import settings
from django.core import signing

from otodb.account.models import Account
from otodb_next.middleware import _SESSION_SALT, SessionAuthMiddleware, User

PASSWORD_HASH = 'pbkdf2_sha256$fake$hash'


def auth_hash(password: str = PASSWORD_HASH) -> str:
	# settings.SECRET_KEY and the middleware's env read resolve to the same
	# value by construction (same env var, same default).
	return Account(password=password).get_session_auth_hash()


def encode_session(session_dict: dict) -> str:
	from django.contrib.sessions.serializers import JSONSerializer

	return signing.dumps(
		session_dict,
		key=settings.SECRET_KEY,
		salt=_SESSION_SALT,
		serializer=JSONSerializer,
		compress=True,
	)


def session_row(session_dict: dict, expires_in_days: int = 14) -> dict:
	return {
		'session_data': encode_session(session_dict),
		'expire_date': datetime.now(timezone.utc) + timedelta(days=expires_in_days),
	}


def user_row(**overrides) -> dict:
	row = {
		'id': 1,
		'username': 'user',
		'level': 20,
		'password': PASSWORD_HASH,
		'is_active': True,
	}
	return row | overrides


class FakeResult:
	def __init__(self, row):
		self._row = row

	def mappings(self):
		return self

	def one_or_none(self):
		return self._row


class FakeSession:
	"""Returns the queued rows in execution order."""

	def __init__(self, rows):
		self._rows = rows

	async def execute(self, query, params):
		return FakeResult(self._rows.pop(0))

	async def __aenter__(self):
		return self

	async def __aexit__(self, *exc):
		return False


def authenticate(rows, cookie='sessionkey123'):
	connection = SimpleNamespace(
		cookies={'sessionid': cookie} if cookie else {},
		scope={
			'app': SimpleNamespace(
				state=SimpleNamespace(
					session_maker_class=lambda: FakeSession(list(rows))
				)
			)
		},
	)
	middleware = SessionAuthMiddleware(app=None)
	return asyncio.run(middleware.authenticate_request(connection))


def test_valid_session_authenticates():
	rows = [
		session_row({'_auth_user_id': '1', '_auth_user_hash': auth_hash()}),
		user_row(),
	]
	result = authenticate(rows)
	assert result.user == User(id=1, username='user', level=20)
	assert result.auth == 'sessionkey123'


def test_no_cookie_is_anonymous_without_db_access():
	result = authenticate([], cookie=None)
	assert result.user is None


def test_missing_session_row_is_anonymous():
	assert authenticate([None]).user is None


def test_expired_session_is_anonymous():
	rows = [
		session_row(
			{'_auth_user_id': '1', '_auth_user_hash': auth_hash()}, expires_in_days=-1
		),
		user_row(),
	]
	assert authenticate(rows).user is None


def test_tampered_session_data_is_anonymous():
	row = session_row({'_auth_user_id': '1', '_auth_user_hash': auth_hash()})
	row['session_data'] = row['session_data'][:-2] + 'xx'
	assert authenticate([row, user_row()]).user is None


def test_unauthenticated_session_is_anonymous():
	# Sessions exist for anonymous visitors too; no _auth_user_id inside.
	assert authenticate([session_row({'foo': 'bar'})]).user is None


def test_deleted_user_is_anonymous():
	rows = [
		session_row({'_auth_user_id': '1', '_auth_user_hash': auth_hash()}),
		None,
	]
	assert authenticate(rows).user is None


def test_deactivated_user_is_anonymous():
	# Django's ModelBackend.user_can_authenticate: is_active=False sessions
	# are anonymous even though the auth hash still matches.
	rows = [
		session_row({'_auth_user_id': '1', '_auth_user_hash': auth_hash()}),
		user_row(is_active=False),
	]
	assert authenticate(rows).user is None


def test_password_change_invalidates_session():
	# The session's auth hash was computed from the old password.
	rows = [
		session_row(
			{'_auth_user_id': '1', '_auth_user_hash': auth_hash('old-password')}
		),
		user_row(),
	]
	assert authenticate(rows).user is None


def test_missing_auth_hash_is_anonymous():
	# Django's get_user treats an absent/empty hash as unverified.
	rows = [
		session_row({'_auth_user_id': '1'}),
		user_row(),
	]
	assert authenticate(rows).user is None
