import enum
from collections.abc import AsyncGenerator

from project.asgi import application as otodb_django

from sqlalchemy import select, func, String, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from litestar import Litestar, get, asgi, Router
from litestar.types import Receive, Scope, Send
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.exceptions import ClientException
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from litestar_granian import GranianPlugin


class Base(DeclarativeBase): ...


db_config = SQLAlchemyAsyncConfig(
	connection_string='sqlite+aiosqlite:///db.sqlite3',
	metadata=Base.metadata,
	create_all=True,
)


class Rating(enum.Enum):
	GENERAL = 0
	SENSITIVE = 1
	EXPLICIT = 2


class TagWorkInstance(Base):
	__tablename__ = 'otodb_tagworkinstance'
	id: Mapped[int] = mapped_column(primary_key=True)
	work_id: Mapped[int] = mapped_column(ForeignKey('otodb_mediawork.id'))
	work_tag_id: Mapped[int] = mapped_column(ForeignKey('otodb_tagwork.id'))
	used_as_source: Mapped[bool]
	creator_roles: Mapped[int | None]
	instance_imported_from_source: Mapped[bool]


class TagWork(Base):
	__tablename__ = 'otodb_tagwork'
	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]
	slug: Mapped[str]
	count: Mapped[int]
	protected: Mapped[bool]
	aliased_to_id: Mapped[int | None]
	deprecated: Mapped[bool]
	category: Mapped[int]
	media_type: Mapped[int | None]


class MediaWork(Base):
	__tablename__ = 'otodb_mediawork'
	id: Mapped[int] = mapped_column(primary_key=True)
	title: Mapped[str | None] = mapped_column(String(1000))
	description: Mapped[str | None]
	rating: Mapped[int] = mapped_column(default=Rating.GENERAL)
	thumbnail_source_id: Mapped[int | None]
	moved_to_id: Mapped[int | None] = mapped_column(ForeignKey('otodb_mediawork.id'))
	_thumbnail: Mapped[str | None] = mapped_column(String(200))
	tags: Mapped[list[TagWork]] = relationship(
		secondary='otodb_tagworkinstance', lazy='selectin'
	)


class MediaSong(Base):
	__tablename__ = 'otodb_mediasong'
	id: Mapped[int] = mapped_column(primary_key=True)
	title: Mapped[str]
	author: Mapped[str]
	variable_bpm: Mapped[bool]
	bpm: Mapped[float | None]
	work_tag_id = Mapped[int]


class Pool(Base):
	__tablename__ = 'otodb_pool'
	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]
	description: Mapped[str]
	author: Mapped[int]


@get('work')
async def work(work_id: int, transaction: AsyncSession) -> MediaWork:
	work = await transaction.scalars(select(MediaWork).where(MediaWork.id == work_id))
	return work.one()


work_router = Router(path='/work', route_handlers=[work])


@get('/stats')
async def stats(transaction: AsyncSession) -> dict[str, int]:
	r = await transaction.execute(
		select(
			select(func.count())
			.select_from(MediaWork)
			.where(MediaWork.moved_to_id != None)
			.label('1'),
			select(func.count()).select_from(TagWork).label('2'),
			select(func.count()).select_from(MediaSong).label('3'),
			select(func.count()).select_from(Pool).label('4'),
		)
	)
	return list(r.one())


api_router = Router(path='/api', route_handlers=[stats, work_router])


@asgi('/v1/', is_mount=True, copy_scope=True)
async def django_app(scope: Scope, receive: Receive, send: Send) -> None:
	if not scope['raw_path'].decode('utf-8').endswith('/') and scope['path'].endswith(
		'/'
	):
		scope['path'] = scope['path'][:-1]
	scope['root_path'] = '/v1/'
	await otodb_django(scope, receive, send)


async def provide_transaction(
	db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
	try:
		async with db_session.begin():
			yield db_session

	except IntegrityError as exc:
		raise ClientException(
			status_code=HTTP_409_CONFLICT,
			detail=str(exc),
		) from exc


app = Litestar(
	route_handlers=[django_app, api_router],
	dependencies={'transaction': provide_transaction},
	plugins=[SQLAlchemyPlugin(db_config), GranianPlugin()],
)
