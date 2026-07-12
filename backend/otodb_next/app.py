from __future__ import annotations

import os
from typing import TYPE_CHECKING

from django.conf import settings
from litestar import Litestar, Router, get
from litestar.config.cors import CORSConfig
from litestar.datastructures import CacheControlHeader
from litestar.openapi import OpenAPIConfig
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

from otodb_next.middleware import (
	CrossOriginProtectionMiddleware,
	SessionAuthMiddleware,
)

if TYPE_CHECKING:
	from sqlalchemy.ext.asyncio import AsyncSession

# project.settings is the single config source while Django is still around;
# it loads .env and derives everything from the environment.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

cors_config = CORSConfig(
	allow_origins=settings.CORS_ALLOWED_ORIGINS,
	allow_origin_regex='.*' if settings.DEBUG else None,
	allow_credentials=True,
	allow_methods=['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT'],
	allow_headers=[
		'accept',
		'authorization',
		'content-type',
		'user-agent',
		'x-csrftoken',
		'x-requested-with',
	],
	max_age=86400,
)


@get('/stats', cache=60, cache_control=CacheControlHeader(max_age=60))
async def statistics(db_session: AsyncSession) -> tuple[int, int, int, int]:
	query = text("""
		SELECT
			(SELECT COUNT(*) FROM otodb_mediawork WHERE otodb_mediawork.moved_to_id IS NULL),
			(SELECT COUNT(*) FROM otodb_tagwork WHERE otodb_tagwork.aliased_to_id IS NULL),
			(SELECT COUNT(*) FROM otodb_mediasong),
			(SELECT COUNT(*) FROM otodb_pool);
	""")
	result = await db_session.execute(query)
	return tuple(result.one())


class Base(DeclarativeBase): ...


_db = settings.DATABASES['default']
if _db['ENGINE'] == 'django.db.backends.sqlite3':
	conn = 'sqlite:///:memory:'
else:
	conn = f'postgresql+psycopg://{_db["USER"]}:{_db["PASSWORD"]}@{_db["HOST"]}:{_db["PORT"]}/{_db["NAME"]}'
config = SQLAlchemyAsyncConfig(
	connection_string=conn,
	create_all=False,
	metadata=Base.metadata,
)

api = Router(path='/api', route_handlers=[statistics])
app = Litestar(
	route_handlers=[api],
	cors_config=cors_config,
	middleware=[CrossOriginProtectionMiddleware(), SessionAuthMiddleware],
	openapi_config=None
	if settings.OTODB_PROTECT_API_DOCS
	else OpenAPIConfig(title='otoDB', version='1'),
	plugins=[SQLAlchemyPlugin(config=config)],
	debug=settings.DEBUG,
)
