from __future__ import annotations

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from litestar import Litestar, Request, Router, get
from litestar.connection import ASGIConnection
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
if TYPE_CHECKING:
	from sqlalchemy.ext.asyncio import AsyncSession


@get('/stats')
async def statistics(
	db_session: AsyncSession, request: Request
) -> tuple[int, int, int, int]:
	print(request.user)
	query = text("""
		SELECT
			(SELECT COUNT(*) FROM otodb_mediawork WHERE otodb_mediawork.moved_to_id IS NULL),
			(SELECT COUNT(*) FROM otodb_tagwork WHERE otodb_tagwork.aliased_to_id IS NULL),
			(SELECT COUNT(*) FROM otodb_mediasong),
			(SELECT COUNT(*) FROM otodb_pool);
	""")
	result = await db_session.execute(query)
	return tuple(result.one())


api = Router(path='/api', route_handlers=[statistics])


class Base(DeclarativeBase): ...


class SessionAuthMiddleware(AbstractAuthenticationMiddleware):
	async def authenticate_request(
		self, connection: ASGIConnection
	) -> AuthenticationResult:
		from datetime import datetime, timezone

		from django.contrib.sessions.serializers import JSONSerializer
		from django.core import signing

		session_key = connection.cookies.get('sessionid')
		if not session_key:
			return AuthenticationResult()
		session_maker = connection.scope['app'].state.session_maker_class
		async with session_maker() as session:
			query = text("""
				SELECT session_data, expire_date
				FROM django_session
				WHERE session_key = :key
			""")
			result = await session.execute(query, {'key': session_key})
			row = result.mappings().one_or_none()

		if not row or row['expire_date'] < datetime.now(timezone.utc):
			return AuthenticationResult()

		try:
			session_dict = signing.loads(
				row['session_data'],
				salt='django.contrib.sessions.SessionStore',
				serializer=JSONSerializer,
			)
		except Exception:
			return AuthenticationResult()

		user_id = session_dict.get('_auth_user_id')

		if not user_id:
			return AuthenticationResult()

		async with session_maker() as session:
			user_query = text(
				'SELECT id, username, level FROM account_account WHERE id = :id'
			)
			user_result = await session.execute(user_query, {'id': int(user_id)})
			user_row = user_result.mappings().one()

		return AuthenticationResult(user=dict(user_row), auth=session_key)


if os.environ.get('OTODB_SKIP_DB'):
	conn = 'sqlite:///:memory:'
else:
	conn = f'postgresql+psycopg://{os.environ["OTODB_DB_USER"]}:{os.environ["OTODB_DB_PASSWORD"]}@{os.environ["OTODB_DB_HOST"]}/{os.environ["OTODB_DB_NAME"]}'
config = SQLAlchemyAsyncConfig(
	connection_string=conn,
	create_all=False,
	metadata=Base.metadata,
)
app = Litestar(
	route_handlers=[api],
	plugins=[SQLAlchemyPlugin(config=config)],
	middleware=[SessionAuthMiddleware],
	debug=os.environ.get('OTODB_DEBUG', 'False').lower() == 'true',
)
