import logging
from datetime import timedelta

from django.core.mail import send_mail
from django.tasks import default_task_backend, task
from django.utils import timezone

logger = logging.getLogger(__name__)


def enqueue_deferred(task_obj, *args, delay: timedelta):
	"""Enqueue a task with run_after, skipping if the backend doesn't support defer."""
	if not default_task_backend.supports_defer:
		return
	task_obj.using(run_after=timezone.now() + delay).enqueue(*args)


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
	"""Delist a work once its moderation window has elapsed."""
	from otodb.account.models import Account
	from otodb.api.work import resolve_work
	from otodb.models import MediaWork
	from otodb.models.enums import Status

	try:
		work = MediaWork.objects.get(id=work_id)
	except MediaWork.DoesNotExist:
		return

	if work.status == Status.PENDING:
		resolve_work(work, by=Account.get_system(), reason='Auto-expired')


@task
def resolve_expired_flag(event_id: int):
	"""Delist a flagged work whose pending flag was never actioned in time."""
	from otodb.account.models import Account
	from otodb.api.work import resolve_work
	from otodb.models import ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType

	try:
		event = ModerationEvent.objects.select_related('work').get(
			id=event_id, event_type=ModerationEventType.FLAG
		)
	except ModerationEvent.DoesNotExist:
		return

	if event.status == FlagStatus.PENDING and event.work:
		resolve_work(
			event.work,
			by=Account.get_system(),
			reason='Auto-delisted (flag expired)',
		)


@task
def resolve_expired_appeal(event_id: int):
	"""Re-delist a work whose pending appeal was never actioned in time."""
	from otodb.account.models import Account
	from otodb.api.work import resolve_work
	from otodb.models import ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType

	try:
		event = ModerationEvent.objects.select_related('work').get(
			id=event_id, event_type=ModerationEventType.APPEAL
		)
	except ModerationEvent.DoesNotExist:
		return

	if event.status == FlagStatus.PENDING and event.work:
		resolve_work(
			event.work,
			by=Account.get_system(),
			reason='Auto-delisted (appeal expired)',
		)


@task
def resolve_expired_source_task(source_id: int):
	"""Auto-reject a pending source once its moderation window has elapsed."""
	from otodb.account.models import Account
	from otodb.api.source import reject_pending_source
	from otodb.models.work_source import WorkSource

	try:
		src = WorkSource.objects.get(id=source_id)
	except WorkSource.DoesNotExist:
		return

	if src.is_pending:
		reject_pending_source(src, by=Account.get_system(), reason='Auto-expired')
