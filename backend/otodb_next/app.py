from __future__ import annotations

import os
from typing import TYPE_CHECKING, NoReturn

from django.conf import settings
from litestar import Litestar, Router, get
from litestar.config.cors import CORSConfig
from litestar.datastructures import CacheControlHeader
from litestar.openapi import OpenAPIConfig
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import text
from sqlalchemy.engine import URL

from otodb.tasks import prune_expired
from otodb_next import revisions
from otodb_next.api.common import user_is_admin
from otodb_next.api.source import source_router
from otodb_next.errors import exception_handlers
from otodb_next.middleware import (
	CrossOriginProtectionMiddleware,
	SessionAuthMiddleware,
)
from otodb_next.models import Base
from otodb_next.openapi import EnumVarnamesPlugin
from otodb_next.scheduler import Job, scheduler
from otodb_next.throttling import build_stores, build_throttles

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


@get(
	'/stats',
	cache=60,
	cache_control=CacheControlHeader(max_age=60),
	opt={'exclude_from_auth': True},
)
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


class _ImportOnlyConfig(SQLAlchemyAsyncConfig):
	def get_engine(self) -> NoReturn:
		raise RuntimeError(
			'otoDB requires Postgres; OTODB_SKIP_DB only supports '
			'importing the app (e.g. manage.py openapi_schema), not serving it'
		)


_db = settings.DATABASES['default']
if _db['ENGINE'] == 'django.db.backends.sqlite3':
	config = _ImportOnlyConfig(connection_string='postgresql+psycopg://')
else:
	# Django normalizes absent keys to '' (service-file config sets none of
	# them); URL.create omits None components and escapes the rest
	_opts = _db.get('OPTIONS', {})
	conn = URL.create(
		'postgresql+psycopg',
		username=_db.get('USER') or None,
		password=_db.get('PASSWORD') or None,
		host=_db.get('HOST') or None,
		port=int(_db['PORT']) if _db.get('PORT') else None,
		database=_db.get('NAME') or None,
		# pg service-file config reaches psycopg as connect() kwargs
		query={k: _opts[k] for k in ('service', 'passfile') if k in _opts},
	).render_as_string(hide_password=False)
	config = SQLAlchemyAsyncConfig(
		connection_string=conn,
		create_all=False,
		metadata=Base.metadata,
	)

jobs = [
	Job('moderation sweep', interval=15 * 60, run=prune_expired),
]

throttles = build_throttles()

api = Router(path='/api', route_handlers=[statistics, source_router])
app = Litestar(
	route_handlers=[api],
	cors_config=cors_config,
	# throttles come after auth: they key on the resolved user
	middleware=[
		CrossOriginProtectionMiddleware(),
		SessionAuthMiddleware,
		*(t.middleware for t in throttles),
	],
	stores=build_stores(),
	exception_handlers=exception_handlers,
	# ninja parity for OTODB_PROTECT_API_DOCS (docs_decorator=staff_member_required,
	# and Account.is_staff is is_admin); the schema itself is always generated so
	# `manage.py openapi_schema` works in every environment.
	openapi_config=OpenAPIConfig(
		title='otoDB',
		version='1',
		openapi_router=Router(
			path='/schema',
			route_handlers=[],
			include_in_schema=False,
			guards=[user_is_admin],
		)
		if settings.OTODB_PROTECT_API_DOCS
		else None,
	),
	plugins=[SQLAlchemyPlugin(config=config), EnumVarnamesPlugin()],
	on_startup=[revisions.load_content_types],
	lifespan=[scheduler(jobs, config.get_engine)],
	debug=settings.DEBUG,
)
