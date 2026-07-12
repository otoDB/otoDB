import os

from otodb_next.app import app as otodb_new
from project.asgi import application as otodb_old


async def application(scope, receive, send):
	from django.urls import Resolver404, resolve

	# Django only handles http; websocket/lifespan scopes go to Litestar
	if scope['type'] != 'http':
		await otodb_new(scope, receive, send)
		return
	try:
		resolve(scope.get('path', '/'))
	except Resolver404:
		await otodb_new(scope, receive, send)
	else:
		await otodb_old(scope, receive, send)


if trusted_hosts := os.environ.get('OTODB_TRUSTED_PROXY_HOSTS'):
	from granian.utils.proxies import wrap_asgi_with_proxy_headers

	application = wrap_asgi_with_proxy_headers(
		application,
		trusted_hosts=[h.strip() for h in trusted_hosts.split(',')],
	)
