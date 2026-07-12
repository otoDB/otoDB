"""Rate limiting for the migrated API -- the port of the ninja throttle stack
(otodb/api/__init__.py):

- anon: anonymous requests only, keyed by client IP (default 20/s)
- auth: every request, keyed by user id, anonymous falls back to IP (40/s)
- write: mutating methods only, same keying as auth (5/s)

Three Litestar RateLimitConfigs -- the same sliding-history algorithm ninja
uses, but declarative (pluggable identifier + check handler, no subclassing).
Histories live in Valkey (same server the Django side uses for its throttles --
rate limits are cache semantics, the one sanctioned Valkey use), namespaced
per scope, expiry via native TTL. Without OTODB_VALKEY_URL (dev, tests) the
stores fall back to in-memory, per-worker -- same posture as the Django side,
which only gets a shared cache when Valkey is configured.

429 responses take ninja's shape ({"code": 429}) via otodb_next.errors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.middleware.rate_limit import RateLimitConfig, get_remote_address
from litestar.stores.memory import MemoryStore
from litestar.stores.valkey import ValkeyStore

if TYPE_CHECKING:
	from litestar import Request
	from litestar.middleware.rate_limit import DurationUnit
	from litestar.stores.base import Store

WRITE_METHODS = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})
_SCOPES = ('throttle_anon', 'throttle_auth', 'throttle_write')
_UNSET = object()


def _user_or_ip(request: Request) -> str:
	# scope.get rather than request.user so the configs also work in tests
	# without the auth middleware; in the app, user is set on every request
	user = request.scope.get('user')
	return f'user:{user.id}' if user is not None else get_remote_address(request)


def _is_anonymous(request: Request) -> bool:
	return request.scope.get('user') is None


def _is_write(request: Request) -> bool:
	return request.method in WRITE_METHODS


def build_throttles(
	*, anon: int = 20, auth: int = 40, write: int = 5, unit: DurationUnit = 'second'
) -> tuple[RateLimitConfig, ...]:
	"""The three throttle configs; rates/unit parameterizable for tests.
	set_rate_limit_headers=False mirrors ninja (flip on for standard
	RateLimit-* response headers if the frontend ever wants backoff info).
	"""
	common = {
		'exclude': ['^/schema'],
		'set_rate_limit_headers': False,
	}
	return (
		RateLimitConfig(
			rate_limit=(unit, anon),
			check_throttle_handler=_is_anonymous,
			store='throttle_anon',
			**common,
		),
		RateLimitConfig(
			rate_limit=(unit, auth),
			identifier_for_request=_user_or_ip,
			store='throttle_auth',
			**common,
		),
		RateLimitConfig(
			rate_limit=(unit, write),
			identifier_for_request=_user_or_ip,
			check_throttle_handler=_is_write,
			store='throttle_write',
			**common,
		),
	)


def build_stores(url: str | None = _UNSET) -> dict[str, Store]:  # type: ignore[assignment]
	"""One store per throttle scope, for Litestar(stores=...): Valkey-backed
	and namespaced when a URL is configured, in-memory otherwise.
	"""
	if url is _UNSET:
		from django.conf import settings

		url = settings.OTODB_VALKEY_URL
	if url:
		base = ValkeyStore.with_client(url=url, namespace='otodb')
		return {scope: base.with_namespace(scope) for scope in _SCOPES}
	return {scope: MemoryStore() for scope in _SCOPES}
