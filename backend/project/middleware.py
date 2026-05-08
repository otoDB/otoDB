from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import (
	get_cache_key,
	get_max_age,
	learn_cache_key,
	patch_response_headers,
)

CACHE_TIMEOUT = 60
KEY_PREFIX = 'anon_api'

# Paths cached for everyone, including authenticated users. These responses
# don't vary by user, language, or origin, so they use a deterministic
# path+query key and skip Django's Vary-aware machinery.
ALWAYS_CACHE_PREFIXES = (
	'/api/stats',
	'/sitemap.xml',
)

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


class AnonymousReadOnlyCacheMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def _eligibility(self, request):
		"""Return ``'always'``, ``'anon'``, or ``None`` for not eligible."""
		if request.method not in ('GET', 'HEAD'):
			return None
		if any(request.path.startswith(p) for p in ALWAYS_CACHE_PREFIXES):
			return 'always'
		if request.COOKIES.get('sessionid'):
			return None
		if any(request.path.startswith(p) for p in BYPASS_PREFIXES):
			return None
		return 'anon'

	def __call__(self, request):
		mode = self._eligibility(request)

		if mode == 'always':
			cache_key = _always_cache_key(request)
		elif mode == 'anon':
			cache_key = get_cache_key(
				request, key_prefix=KEY_PREFIX, method=request.method
			)
		else:
			cache_key = None

		if cache_key is not None:
			cached = cache.get(cache_key)
			if cached is not None:
				return _unpack(cached)

		response = self.get_response(request)

		if (
			mode is not None
			and response.status_code == 200
			and not response.has_header('Set-Cookie')
		):
			timeout = get_max_age(response) or CACHE_TIMEOUT
			patch_response_headers(response, timeout)
			if mode == 'always':
				cache.set(_always_cache_key(request), _pack(response), timeout)
			else:
				cache.set(
					learn_cache_key(request, response, timeout, KEY_PREFIX),
					_pack(response),
					timeout,
				)

		return response
