from collections.abc import AsyncGenerator

from project.asgi import application as otodb_django

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from litestar import Litestar, get, asgi, Router
from litestar.types import Receive, Scope, Send
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.exceptions import ClientException, NotFoundException
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin

from litestar_granian import GranianPlugin

class Base(DeclarativeBase): ...

db_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///db.sqlite3", metadata=Base.metadata, create_all=True
)

class MediaWork(Base):
    __tablename__ = "otodb_mediawork"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    rating: Mapped[int]
    _thumbnail = Mapped[str | None]
    thumbnail_source_id: Mapped[int | None]
    moved_to_id = Mapped[int | None]

class MediaSong(Base):
    __tablename__ = "otodb_mediasong"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]
    variable_bpm: Mapped[bool]
    bpm: Mapped[float | None]
    work_tag_id = Mapped[int]

class TagWork(Base):
    __tablename__ = "otodb_tagwork"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    slug: Mapped[str]
    count: Mapped[int]
    protected: Mapped[bool]
    alised_to_id: Mapped[int | None]
    deprecated: Mapped[bool]
    category: Mapped[int]
    media_type: Mapped[int | None]

class Pool(Base):
    __tablename__ = "otodb_pool"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    author: Mapped[int]

@get("/stats")
async def stats(transaction: AsyncSession) -> dict[str, int]:
    return [
        await transaction.scalar(select(func.count()).select_from(MediaWork).where(MediaWork.moved_to_id != None)),
        await transaction.scalar(select(func.count()).select_from(TagWork)),
        await transaction.scalar(select(func.count()).select_from(MediaSong)),
        await transaction.scalar(select(func.count()).select_from(Pool)),
    ]

api_router = Router(path="/api", route_handlers=[stats])

@asgi('/v1/', is_mount=True, copy_scope=True)
async def django_app(scope: Scope, receive: Receive, send: Send) -> None:
    if not scope['raw_path'].decode('utf-8').endswith('/') and scope['path'].endswith('/'):
        scope['path'] = scope['path'][:-1]
    scope['root_path'] = '/v1/'
    await otodb_django(scope, receive, send)

async def provide_transaction(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
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
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config), GranianPlugin()],
)
