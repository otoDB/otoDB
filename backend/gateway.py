from otodb_next.app import app as otodb_new
from project.asgi import application as otodb_old


async def application(scope, receive, send):
	from django.urls import Resolver404, resolve

	if scope['type'] not in ('http', 'websocket'):
		await otodb_new(scope, receive, send)
		return
	try:
		resolve(scope.get('path', '/'))
		await otodb_old(scope, receive, send)
	except Resolver404:
		await otodb_new(scope, receive, send)
