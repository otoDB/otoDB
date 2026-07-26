from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import get_max_age, patch_response_headers

CACHE_TIMEOUT = 60
KEY_PREFIX = 'anon_api'

# Paths cached for everyone, including authenticated users, with per-prefix
# timeouts in seconds.
ALWAYS_CACHE_PREFIXES = {
	'/api/stats': 60,
	'/sitemap.xml': 3600,
}

# Paths never cached (auth-sensitive or admin surfaces).
BYPASS_PREFIXES = (
	'/api/auth',
	'/api/profile',
	'/api/moderation',
	'/admin',
	'/silk',
)


# HttpResponse isn't msgpack-serializable; round-trip through a small dict so
# the default ormsgpack serializer keeps working.
def _pack(response: HttpResponse) -> dict:
	return {
		'content': bytes(response.content),
		'status': response.status_code,
		'headers': list(response.headers.items()),
	}


def _unpack(data: dict) -> HttpResponse:
	return HttpResponse(
		content=data['content'],
		status=data['status'],
		headers=dict(data['headers']),
	)


def _always_cache_key(request) -> str:
	return f'{KEY_PREFIX}:always:{request.method}:{request.get_full_path()}'


def _anon_cache_key(request) -> str:
	origin = request.headers.get('Origin', '')
	return f'{KEY_PREFIX}:anon:{request.method}:{origin}:{request.get_full_path()}'


class AnonymousReadOnlyCacheMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def _always_timeout(self, request) -> int | None:
		for prefix, timeout in ALWAYS_CACHE_PREFIXES.items():
			if request.path.startswith(prefix):
				return timeout
		return None

	def _is_anon_eligible(self, request) -> bool:
		if request.COOKIES.get('sessionid'):
			return False
		if any(request.path.startswith(p) for p in BYPASS_PREFIXES):
			return False
		return True

	def __call__(self, request):
		always_timeout: int | None = None
		cache_key = None

		if request.method in ('GET', 'HEAD'):
			always_timeout = self._always_timeout(request)
			if always_timeout is not None:
				cache_key = _always_cache_key(request)
			elif self._is_anon_eligible(request):
				cache_key = _anon_cache_key(request)

		if cache_key is not None:
			cached = cache.get(cache_key)
			if cached is not None:
				return _unpack(cached)

		response = self.get_response(request)

		if response.status_code != 200 or response.has_header('Set-Cookie'):
			return response

		if always_timeout is not None:
			patch_response_headers(response, always_timeout)
			cache.set(cache_key, _pack(response), always_timeout)
		elif cache_key is not None:
			timeout = get_max_age(response) or CACHE_TIMEOUT
			patch_response_headers(response, timeout)
			cache.set(cache_key, _pack(response), timeout)

		return response
