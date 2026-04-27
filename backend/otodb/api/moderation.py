from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import field_validator

from otodb.account.models import Account
from otodb.models import ModerationEvent
from otodb.models.enums import FlagStatus, ModerationAction, ModerationEventType

moderation_router = Router()


class ModerationEventBySchema(Schema):
	id: str
	username: str

	@field_validator('id', mode='before')
	@classmethod
	def _coerce_id(cls, v):
		return str(v)


class ModerationEventSchema(Schema):
	event_type: ModerationEventType
	event_id: str
	work_id: str | None
	source_id: str | None
	by: ModerationEventBySchema | None
	reason: str
	status: FlagStatus | ModerationAction | None
	event_at: datetime

	@field_validator('event_id', 'source_id', mode='before')
	@classmethod
	def _coerce_ids(cls, v):
		return str(v) if v is not None else None


class ModerationEventResponse(Schema):
	items: list[ModerationEventSchema]
	count: int


@moderation_router.get('events', response=ModerationEventResponse)
def moderation_events(
	request: HttpRequest,
	work_id: str | None = None,
	source_id: str | None = None,
	user_id: str | None = None,
	limit: int = 30,
	offset: int = 0,
):
	user = request.user if request.user.is_authenticated else None
	is_editor = user is not None and user.level >= Account.Levels.EDITOR

	if (
		user_id is not None
		and not is_editor
		and (user is None or user_id != str(user.pk))
	):
		raise HttpError(403, 'Forbidden')

	qs = ModerationEvent.objects.select_related('by').order_by('-date')

	if work_id is not None:
		qs = qs.filter(work_id=work_id)
	if source_id is not None:
		qs = qs.filter(source_id=int(source_id))
	if user_id is not None:
		qs = qs.filter(by_id=user_id)

	count = qs.count()
	events = list(qs[offset : offset + min(limit, 30)])

	items = []
	for e in events:
		is_own = user is not None and e.by_id == user.pk
		hide_author = e.event_type in (
			ModerationEventType.FLAG,
			ModerationEventType.DISAPPROVAL,
		)
		show_by = is_editor or is_own or not hide_author
		show_reason = show_by or e.event_type != ModerationEventType.DISAPPROVAL
		items.append(
			{
				'event_type': e.event_type,
				'event_id': e.pk,
				'work_id': e.work_id,
				'source_id': e.source_id,
				'by': {'id': e.by_id, 'username': e.by.username} if show_by else None,
				'reason': (e.reason or '') if show_reason else '',
				'status': e.status,
				'event_at': e.date,
			}
		)

	return {'items': items, 'count': count}
