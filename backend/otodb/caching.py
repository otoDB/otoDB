from django.http import HttpResponse, HttpResponseBase
from django_vcache.backend import ValkeyCache

_HTTP_RESPONSE_TAG = '__django_http_response__'


def _serialize_http_response(response: HttpResponseBase) -> dict:
	return {
		_HTTP_RESPONSE_TAG: True,
		'content': bytes(response.content),
		'status': response.status_code,
		'reason': response._reason_phrase,
		'charset': response._charset,
		'headers': list(response.headers.items()),
		'cookies': response.cookies.output(header='', sep='\n').strip(),
	}


def _deserialize_http_response(data: dict) -> HttpResponse:
	response = HttpResponse(
		content=data['content'],
		status=data['status'],
		reason=data['reason'],
		charset=data['charset'],
		headers=dict(data['headers']),
	)
	if data['cookies']:
		response.cookies.load(data['cookies'])
	return response


class HttpAwareValkeyCache(ValkeyCache):
	"""ValkeyCache that transparently round-trips Django HttpResponse objects.

	Allows ``@cache_page`` / ``UpdateCacheMiddleware`` to keep using the
	default msgpack serializer. HttpResponse is decomposed into a
	msgpack-friendly dict on store and reconstructed on read; everything else
	flows through ormsgpack unchanged.
	"""

	def __init__(self, server, params):
		super().__init__(server, params)
		_orig_dumps = self._dumps
		_orig_loads = self._loads

		def dumps(value):
			if isinstance(value, HttpResponseBase):
				value = _serialize_http_response(value)
			return _orig_dumps(value)

		def loads(data):
			value = _orig_loads(data)
			if isinstance(value, dict) and value.get(_HTTP_RESPONSE_TAG):
				return _deserialize_http_response(value)
			return value

		self._dumps = dumps
		self._loads = loads
