from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.conf import settings
from litestar import Litestar, Router, get
from litestar.config.cors import CORSConfig
from litestar.datastructures import CacheControlHeader
from litestar.openapi import OpenAPIConfig
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

from otodb.tasks import prune_expired
from otodb_next.middleware import (
	CrossOriginProtectionMiddleware,
	SessionAuthMiddleware,
)
from otodb_next.scheduler import Job, scheduler

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


@dataclass
class WorkHistoryPoint:
	"""Works in the database at the end of one UTC day."""

	date: datetime.date
	total: int


# The data has daily granularity, so one hour of cache staleness is not visible.
@get('/stats/works/history', cache=3600, cache_control=CacheControlHeader(max_age=3600))
async def work_history(db_session: AsyncSession) -> list[WorkHistoryPoint]:
	"""Works total at the end of each UTC day, ascending. Quiet days get no point.

	The query excludes merged works (`moved_to`). Thus the last total agrees with
	`/api/stats`, but a merge also decreases the totals of past days.
	"""
	# `AT TIME ZONE 'UTC'` pins the day boundary; a bare `::date` obeys the session
	# TimeZone. `::int` prevents a `Decimal` from the window sum.
	query = text("""
		SELECT
			(created_at AT TIME ZONE 'UTC')::date,
			SUM(COUNT(*)) OVER (ORDER BY (created_at AT TIME ZONE 'UTC')::date)::int
		FROM otodb_mediawork
		WHERE moved_to_id IS NULL
		GROUP BY 1
		ORDER BY 1;
	""")
	result = await db_session.execute(query)
	return [WorkHistoryPoint(*row) for row in result]


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

jobs = [
	Job('moderation sweep', interval=15 * 60, run=prune_expired),
]

api = Router(path='/api', route_handlers=[statistics, work_history])
app = Litestar(
	route_handlers=[api],
	cors_config=cors_config,
	middleware=[CrossOriginProtectionMiddleware(), SessionAuthMiddleware],
	openapi_config=None
	if settings.OTODB_PROTECT_API_DOCS
	else OpenAPIConfig(title='otoDB', version='1'),
	plugins=[SQLAlchemyPlugin(config=config)],
	lifespan=[scheduler(jobs, config.get_engine)],
	debug=settings.DEBUG,
)
