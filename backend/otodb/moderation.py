from otodb.account.models import Account
from otodb.models import MediaWork, ModerationEvent
from otodb.models.enums import (
	FlagStatus,
	ModerationAction,
	ModerationEventType,
	Status,
)


def resolve_work(work: MediaWork, by: Account, reason: str = ''):
	"""Delist a work, dismiss any pending flags/appeals, and record the action."""
	work.moderation_events.filter(
		event_type__in=[ModerationEventType.FLAG, ModerationEventType.APPEAL],
		status=FlagStatus.PENDING,
	).update(status=FlagStatus.REJECTED)
	work.status = Status.DELISTED
	work.save(update_fields=['status'])
	ModerationEvent.objects.create(
		work=work,
		event_type=ModerationEventType.MOD_ACTION,
		status=ModerationAction.WORK_DELISTED,
		by=by,
		reason=reason,
	)
