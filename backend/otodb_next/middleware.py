"""Middleware for the Litestar app: cross-origin (CSRF) protection and
Django-session authentication.

CSRF uses the Sec-Fetch-Site + Origin header approach described in Filippo
Valsorda's article (https://words.filippo.io/csrf/) and implemented in Go
1.25's http.CrossOriginProtection, replacing token-based checks. Django keeps
its own token CSRF for its routes; the frontend's csrftoken/X-CSRFToken
traffic is ignored here.
"""

from __future__ import annotations

import hmac
import logging
import urllib.parse
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import orjson
from litestar.enums import ScopeType
from litestar.middleware import (
	AbstractAuthenticationMiddleware,
	ASGIMiddleware,
	AuthenticationResult,
)
from sqlalchemy import text

if TYPE_CHECKING:
	from litestar.connection import ASGIConnection
	from litestar.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS', 'TRACE'})


class CrossOriginProtectionMiddleware(ASGIMiddleware):
	"""Rejects unsafe-method requests that browsers mark as cross-origin,
	unless the Origin is trusted (the frontend lives on another subdomain).
	Non-browser clients send neither Sec-Fetch-Site nor Origin and pass
	through unchanged -- CSRF is a browser-only attack.

	Handlers can opt out with opt={'csrf_exempt': True}.
	"""

	scopes = (ScopeType.HTTP,)
	exclude_opt_key = 'csrf_exempt'

	def __init__(self, trusted_origins: list[str] | None = None) -> None:
		if trusted_origins is None:
			# project.settings is the single config source while Django exists
			from django.conf import settings

			trusted_origins = list(settings.CSRF_TRUSTED_ORIGINS)
		self.trusted_origins: list[str] = trusted_origins

	async def handle(
		self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
	) -> None:
		# scopes already narrows to http; the type check re-narrows for pyright
		if scope['type'] != 'http' or scope['method'] in SAFE_METHODS:
			await next_app(scope, receive, send)
			return
		reason = self._check(scope)
		if reason is None:
			await next_app(scope, receive, send)
			return
		logger.warning('Forbidden (%s): %s', reason, scope['path'])
		body = orjson.dumps(
			{'status_code': 403, 'detail': f'Cross-origin request denied: {reason}'}
		)
		await send(
			{
				'type': 'http.response.start',
				'status': 403,
				'headers': [
					(b'content-type', b'application/json'),
					(b'content-length', str(len(body)).encode()),
				],
			}
		)
		await send({'type': 'http.response.body', 'body': body, 'more_body': False})

	def _check(self, scope: Scope) -> str | None:
		headers = {k.lower(): v for k, v in scope['headers']}
		origin = (headers.get(b'origin') or b'').decode('latin1')
		if origin and origin in self.trusted_origins:
			return None

		# Primary defense: Sec-Fetch-Site (set by browsers, unforgeable from JS)
		if site_bytes := headers.get(b'sec-fetch-site'):
			site = site_bytes.decode('latin1')
			if site in ('same-origin', 'none'):
				return None
			return f"Sec-Fetch-Site was {site!r}, expected 'same-origin' or 'none'"

		# No Sec-Fetch-Site and no Origin -> non-browser client (curl, SSR proxy)
		if not origin:
			return None

		# Fallback for older browsers: Origin host must match the Host header
		# (host only, like Go -- the scheme is not reliably known behind proxies)
		host = (headers.get(b'host') or b'').decode('latin1')
		parsed = urllib.parse.urlparse(origin)
		origin_host = parsed.hostname or ''
		if parsed.port:
			origin_host = f'{origin_host}:{parsed.port}'
		if host and origin_host == host:
			return None
		return f'Origin {origin!r} does not match Host {host!r} or trusted origins'


_SESSION_QUERY = text("""
	SELECT session_data, expire_date
	FROM django_session
	WHERE session_key = :key
""")

_USER_QUERY = text("""
	SELECT id, username, level, password
	FROM account_account
	WHERE id = :id
""")

_SESSION_SALT = 'django.contrib.sessions.SessionStore'
_AUTH_HASH_SALT = 'django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash'


@dataclass
class User:
	id: int
	username: str
	level: int  # TODO enum


class SessionAuthMiddleware(AbstractAuthenticationMiddleware):
	"""Django-format session auth without Django: reads django_session with
	the app's async engine and verifies with the same signing primitives and
	secret. Both apps share the session format for the whole migration.

	request.user is a User, or None when anonymous. Handlers can skip the
	lookup with opt={'exclude_from_auth': True}.

	TODO: post-Django, swap to Litestar's session store
	"""

	async def authenticate_request(
		self, connection: ASGIConnection
	) -> AuthenticationResult:
		# Django is only needed for its session/signing primitives, which read
		# settings.SECRET_KEY (and fallbacks) themselves.
		from django.contrib.sessions.serializers import JSONSerializer
		from django.core import signing
		from django.utils.crypto import salted_hmac

		anonymous = AuthenticationResult(user=None, auth=None)
		session_key = connection.cookies.get('sessionid')
		if not session_key:
			return anonymous

		session_maker = connection.scope['app'].state.session_maker_class
		async with session_maker() as db:
			result = await db.execute(_SESSION_QUERY, {'key': session_key})
			row = result.mappings().one_or_none()
			if row is None or row['expire_date'] < datetime.now(UTC):
				return anonymous

			try:
				session = signing.loads(
					row['session_data'],
					salt=_SESSION_SALT,
					serializer=JSONSerializer,
				)
			except Exception:  # noqa: BLE001
				# Tampered or truncated session data; Django's SessionBase
				# .decode treats any failure here as an empty session.
				return anonymous

			user_id = session.get('_auth_user_id')
			if not user_id:
				return anonymous

			result = await db.execute(_USER_QUERY, {'id': int(user_id)})
			user = result.mappings().one_or_none()
		if user is None:
			return anonymous

		# Django's get_user: the session stores an HMAC of the password hash,
		# so changing the password invalidates every other session.
		expected = salted_hmac(
			_AUTH_HASH_SALT, user['password'], algorithm='sha256'
		).hexdigest()
		if not hmac.compare_digest(session.get('_auth_user_hash', ''), expected):
			return anonymous

		return AuthenticationResult(
			user=User(id=user['id'], username=user['username'], level=user['level']),
			auth=session_key,
		)
