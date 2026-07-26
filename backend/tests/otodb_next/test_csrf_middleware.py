"""Tests for the cross-origin protection (CSRF) middleware on the Litestar app.

The middleware is driven as a raw ASGI callable so nothing here needs a
running app, a database, or an HTTP client. Semantics under test mirror Go
1.25's net/http.CrossOriginProtection: Sec-Fetch-Site / Origin header checks,
no tokens.
"""

import asyncio
import json
from types import SimpleNamespace

from otodb_next.middleware import CrossOriginProtectionMiddleware


def make_scope(method='POST', headers=None, path='/api/thing', scheme='https'):
	return {
		'type': 'http',
		'method': method,
		'path': path,
		'scheme': scheme,
		'headers': headers or [],
	}


def run(trusted_origins, scope):
	"""Run the middleware over a recording app; returns (next_called, sent)."""
	called = []

	async def next_app(scope, receive, send):
		called.append(scope['path'])
		await send({'type': 'http.response.start', 'status': 200, 'headers': []})
		await send({'type': 'http.response.body', 'body': b'ok'})

	asgi = CrossOriginProtectionMiddleware(trusted_origins=trusted_origins)(next_app)
	sent = []

	async def receive():
		return {'type': 'http.request', 'body': b'', 'more_body': False}

	async def send(message):
		sent.append(message)

	asyncio.run(asgi(scope, receive, send))
	return bool(called), sent


def assert_rejected(sent, reason):
	assert sent[0]['status'] == 403
	detail = json.loads(sent[1]['body'])['detail']
	assert reason in detail


def test_safe_method_skips_checks():
	passed, _ = run(
		[], make_scope(method='GET', headers=[(b'sec-fetch-site', b'cross-site')])
	)
	assert passed


def test_no_browser_headers_passes():
	# curl, scripts, and the SvelteKit SSR proxy send neither header.
	passed, _ = run([], make_scope())
	assert passed


def test_sec_fetch_site_same_origin_passes():
	passed, _ = run([], make_scope(headers=[(b'sec-fetch-site', b'same-origin')]))
	assert passed


def test_sec_fetch_site_none_passes():
	passed, _ = run([], make_scope(headers=[(b'sec-fetch-site', b'none')]))
	assert passed


def test_sec_fetch_site_cross_site_rejected():
	passed, sent = run([], make_scope(headers=[(b'sec-fetch-site', b'cross-site')]))
	assert not passed
	assert_rejected(sent, "Sec-Fetch-Site was 'cross-site'")


def test_sec_fetch_site_same_site_rejected():
	# Subdomains are same-site but different origins; only the trusted list
	# lets them through (Go's CrossOriginProtection makes the same call).
	passed, sent = run([], make_scope(headers=[(b'sec-fetch-site', b'same-site')]))
	assert not passed
	assert_rejected(sent, "Sec-Fetch-Site was 'same-site'")


def test_trusted_origin_beats_sec_fetch_site():
	headers = [
		(b'sec-fetch-site', b'same-site'),
		(b'origin', b'https://otodb.net'),
	]
	passed, _ = run(['https://otodb.net'], make_scope(headers=headers))
	assert passed


def test_untrusted_cross_site_origin_rejected():
	headers = [
		(b'sec-fetch-site', b'cross-site'),
		(b'origin', b'https://evil.example'),
	]
	passed, _ = run(['https://otodb.net'], make_scope(headers=headers))
	assert not passed


def test_origin_matching_host_passes_without_sec_fetch_site():
	# Pre-2023 browser fallback: Origin only, host compared against Host.
	headers = [
		(b'origin', b'https://otodb.net'),
		(b'host', b'otodb.net'),
	]
	passed, _ = run([], make_scope(headers=headers))
	assert passed


def test_origin_not_matching_host_rejected_without_sec_fetch_site():
	headers = [
		(b'origin', b'https://evil.example'),
		(b'host', b'otodb.net'),
	]
	passed, sent = run([], make_scope(headers=headers))
	assert not passed
	assert_rejected(sent, 'does not match Host')


def test_null_origin_rejected():
	headers = [
		(b'origin', b'null'),
		(b'host', b'otodb.net'),
	]
	passed, _ = run([], make_scope(headers=headers))
	assert not passed


def test_trusted_origin_passes_without_sec_fetch_site():
	headers = [
		(b'origin', b'https://otodb.net'),
		(b'host', b'api.otodb.net'),
	]
	passed, _ = run(['https://otodb.net'], make_scope(headers=headers))
	assert passed


def test_csrf_exempt_opt_skips_checks():
	scope = make_scope(headers=[(b'sec-fetch-site', b'cross-site')])
	scope['route_handler'] = SimpleNamespace(opt={'csrf_exempt': True})
	passed, _ = run([], scope)
	assert passed
