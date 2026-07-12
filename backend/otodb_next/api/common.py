"""Endpoint kit for migrated handlers -- the port of otodb/api/common.py's
decorators, so a migrated endpoint reads like its ninja original:

	@put('/origin', guards=[user_is_trusted])
	@track_revision(Route.WORKSOURCE_SET_ORIGIN)
	async def source_origin(request, db_session, source_id: str, ...) -> None:
		src = await get_or_404(db_session, WorkSource, source_id)
		...mutate src...
"""

from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from litestar import Request
from litestar.datastructures import State
from litestar.exceptions import (
	NotAuthorizedException,
	NotFoundException,
	PermissionDeniedException,
	ValidationException,
)
from sqlalchemy.orm import joinedload

from otodb_next.enums import Route, UserLevel
from otodb_next.middleware import User
from otodb_next.revisions import revision_scope

if TYPE_CHECKING:
	from collections.abc import Iterable

	from litestar.connection import ASGIConnection
	from litestar.handlers.base import BaseRouteHandler
	from sqlalchemy.ext.asyncio import AsyncSession

AuthedRequest = Request[User, None, State]

T = TypeVar('T')


def _min_level_guard(level: UserLevel):
	def guard(
		connection: ASGIConnection[Any, User | None, None, State],
		_handler: BaseRouteHandler,
	) -> None:
		user = connection.user
		if user is None:
			raise NotAuthorizedException  # ninja django_auth: 401
		if user.level < level:
			raise PermissionDeniedException  # ninja perm_decorator_ctor: 403

	return guard


# ninja's user_is_trusted is `level > RESTRICTED`; MEMBER is the next level up
user_is_trusted = _min_level_guard(UserLevel.MEMBER)
user_is_editor = _min_level_guard(UserLevel.EDITOR)
user_is_mod = _min_level_guard(UserLevel.MOD)
user_is_admin = _min_level_guard(UserLevel.ADMIN)


def track_revision(route: Route):
	def decorate(fn):
		@wraps(fn)
		async def wrapper(*args, **kwargs):
			request = kwargs['request']
			db_session = kwargs['db_session']
			async with revision_scope(
				db_session, user_id=request.user.id, route=int(route)
			):
				result = await fn(*args, **kwargs)
			await db_session.commit()
			return result

		return wrapper

	return decorate


async def get_or_404(
	session: AsyncSession,
	model: type[T],
	pk: str | int,
	*,
	load: Iterable[Any] = (),
) -> T:
	try:
		pk = int(pk)
	except (TypeError, ValueError) as exc:
		raise ValidationException from exc  # ninja: 422; here 400
	obj = await session.get(model, pk, options=[joinedload(rel) for rel in load])
	if obj is None:
		raise NotFoundException
	return obj
