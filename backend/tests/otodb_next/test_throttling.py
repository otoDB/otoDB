"""Throttle behavior (permanent): ninja-parity 429 shape and read/write budget
isolation. In-memory stores and minute-wide windows keep timing out of the
picture; the Valkey-vs-memory decision is build_stores' concern, exercised in
production wiring.
"""

from litestar import get, post
from litestar.testing import create_test_client

from otodb_next.errors import exception_handlers
from otodb_next.throttling import build_stores, build_throttles


@get('/ping')
async def ping() -> None: ...


@post('/poke')
async def poke() -> None: ...


def _client(**rates):
	return create_test_client(
		[ping, poke],
		middleware=[t.middleware for t in build_throttles(unit='minute', **rates)],
		stores=build_stores(url=None),
		exception_handlers=exception_handlers,
	)


def test_read_throttle_and_429_shape():
	with _client(anon=3, auth=100, write=100) as client:
		for _ in range(3):
			assert client.get('/ping').status_code == 200
		r = client.get('/ping')
		assert (r.status_code, r.json()) == (429, {'code': 429})


def test_write_budget_is_separate():
	with _client(anon=100, auth=100, write=2) as client:
		assert client.get('/ping').status_code == 200
		assert client.post('/poke').status_code == 201
		assert client.post('/poke').status_code == 201
		r = client.post('/poke')
		assert (r.status_code, r.json()) == (429, {'code': 429})
		# the write limit doesn't bleed into reads
		assert client.get('/ping').status_code == 200
