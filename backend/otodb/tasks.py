import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.tasks import default_task_backend, task
from django.utils import timezone

logger = logging.getLogger(__name__)


def enqueue_deferred(task_obj, *args, delay: timedelta):
	"""Enqueue a task with run_after, skipping if the backend doesn't support defer."""
	if not default_task_backend.supports_defer:
		return
	task_obj.using(run_after=timezone.now() + delay).enqueue(*args)


def _system_user():
	from otodb.account.models import Account

	return Account.objects.filter(level=Account.Levels.OWNER).first()


@task
def send_email(
	subject: str,
	body: str,
	from_email: str,
	to: list[str],
) -> None:
	try:
		send_mail(
			subject=subject, message=body, from_email=from_email, recipient_list=to
		)
	except Exception:
		logger.exception('Failed to send email to %s', to)


@task
def resolve_expired_work(work_id: int):
	"""Resolve a single pending work if it's still pending and past the moderation period."""
	from otodb.api.work import resolve_work
	from otodb.models import MediaWork, ModerationEvent
	from otodb.models.enums import (
		ModerationAction,
		ModerationEventType,
		Status,
	)

	try:
		work = MediaWork.objects.get(id=work_id)
	except MediaWork.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if work.status == Status.PENDING and work.created_at < cutoff:
		resolve_work(work)
		system_user = _system_user()
		if system_user:
			ModerationEvent.objects.create(
				work=work,
				event_type=ModerationEventType.MOD_ACTION,
				status=ModerationAction.WORK_DELISTED,
				by=system_user,
				reason='Auto-expired',
			)


@task
def resolve_expired_flag(event_id: int):
	"""Resolve a work with an expired pending flag."""
	from otodb.api.work import resolve_work
	from otodb.models import ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType

	try:
		event = ModerationEvent.objects.select_related('work').get(
			id=event_id, event_type=ModerationEventType.FLAG
		)
	except ModerationEvent.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if event.status == FlagStatus.PENDING and event.date < cutoff and event.work:
		resolve_work(event.work)


@task
def resolve_expired_appeal(event_id: int):
	"""Resolve a work with an expired pending appeal."""
	from otodb.api.work import resolve_work
	from otodb.models import ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType

	try:
		event = ModerationEvent.objects.select_related('work').get(
			id=event_id, event_type=ModerationEventType.APPEAL
		)
	except ModerationEvent.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if event.status == FlagStatus.PENDING and event.date < cutoff and event.work:
		resolve_work(event.work)


@task
def resolve_expired_source_task(source_id: int):
	"""Auto-reject an expired pending source."""
	from otodb.api.source import reject_pending_source
	from otodb.models.work_source import WorkSource

	try:
		src = WorkSource.objects.get(id=source_id)
	except WorkSource.DoesNotExist:
		return

	if not src.is_pending:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if src.created_at < cutoff:
		system_user = _system_user()
		if system_user:
			reject_pending_source(src, by=system_user, reason='Auto-expired')
