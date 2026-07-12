from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Router, put

from otodb_next.api.common import (
	AuthedRequest,
	get_or_404,
	track_revision,
	user_is_trusted,
)
from otodb_next.enums import ErrorCode, Route, Status, UserLevel, WorkOrigin
from otodb_next.errors import ApiError
from otodb_next.models import WorkSource

if TYPE_CHECKING:
	from sqlalchemy.ext.asyncio import AsyncSession

source_router = Router(path='/upload', route_handlers=[])


@put('/origin', operation_id='otodb_api_source_source_origin', guards=[user_is_trusted])
@track_revision(Route.WORKSOURCE_SET_ORIGIN)
async def source_origin(
	request: AuthedRequest,
	db_session: AsyncSession,
	source_id: str,
	status: WorkOrigin,
) -> None:
	src = await get_or_404(db_session, WorkSource, source_id, load=[WorkSource.media])
	is_editor = request.user.level >= UserLevel.EDITOR
	# Trusted users may only set the origin while the work or the source itself
	# is still pending; otherwise an editor is required.
	if (
		src.media is not None
		and not is_editor
		and src.media.status != Status.PENDING
		and not src.is_pending
	):
		raise ApiError(403, ErrorCode.EDITOR_ONLY)
	src.work_origin = int(status)


source_router.register(source_origin)
