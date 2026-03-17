from datetime import datetime

from ninja import Schema, Router
from ninja.security import django_auth

from otodb.models import ModerationEvent
from otodb.models.enums import ModerationEventType
from otodb.account.models import Account

from .common import AuthedHttpRequest


moderation_router = Router()


class ModerationEventBySchema(Schema):
	id: int
	username: str


class ModerationEventSchema(Schema):
	event_type: int
	event_id: int
	work_id: int | None
	source_id: int | None
	by: ModerationEventBySchema | None
	reason: str
	status: int | None
	event_at: datetime


class ModerationEventResponse(Schema):
	items: list[ModerationEventSchema]
	count: int


@moderation_router.get('events', auth=django_auth, response=ModerationEventResponse)
def moderation_events(
	request: AuthedHttpRequest,
	work_id: int | None = None,
	source_id: int | None = None,
	user_id: int | None = None,
	limit: int = 30,
	offset: int = 0,
):
	"""Query the unified moderation events view."""
	qs = ModerationEvent.objects.all().order_by('-event_at')

	if work_id is not None:
		qs = qs.filter(work_id=work_id)
	if source_id is not None:
		qs = qs.filter(source_id=source_id)
	if user_id is not None:
		qs = qs.filter(by_id=user_id)

	is_editor = request.user.level >= Account.Levels.EDITOR

	count = qs.count()
	events = list(qs[offset : offset + min(limit, 30)])

	items = []
	for e in events:
		is_own = e.by_id == request.user.pk
		hide_author = e.event_type in (
			ModerationEventType.FLAG,
			ModerationEventType.DISAPPROVAL,
		)
		show_by = is_editor or is_own or not hide_author
		show_reason = show_by or e.event_type != ModerationEventType.DISAPPROVAL
		items.append(
			{
				'event_type': e.event_type,
				'event_id': e.event_id,
				'work_id': e.work_id,
				'source_id': e.source_id,
				'by': {'id': e.by_id, 'username': e.by_username} if show_by else None,
				'reason': (e.reason or '') if show_reason else '',
				'status': e.status,
				'event_at': e.event_at,
			}
		)

	return {'items': items, 'count': count}
