from __future__ import annotations

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from litestar import Litestar, Router, get
from litestar.di import NamedDependency
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
if TYPE_CHECKING:
	from sqlalchemy.ext.asyncio import AsyncSession


@get('/stats')
async def statistics(
	db_session: NamedDependency[AsyncSession],
) -> tuple[int, int, int, int]:
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


config = SQLAlchemyAsyncConfig(
	connection_string=f'postgresql+psycopg://{os.environ["OTODB_DB_USER"]}:{os.environ["OTODB_DB_PASSWORD"]}@{os.environ["OTODB_DB_HOST"]}/{os.environ["OTODB_DB_NAME"]}',
	create_all=False,
	metadata=Base.metadata,
)
api = Router(path='/api', route_handlers=[statistics])
app = Litestar(
	route_handlers=[api],
	plugins=[SQLAlchemyPlugin(config=config)],
	debug=os.environ.get('OTODB_DEBUG', 'False').lower() == 'true',
)
