import logging
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.mail import send_mail
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

# In-process replacement for the rq worker: fine for webhooks and emails,
# which are allowed to be lost on process death. Anything that must not be
# lost belongs in the database and gets picked up by prune_expired (run
# periodically from the otodb_next lifespan sweep).
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='otodb-task')


def fire_and_forget(fn, /, *args, **kwargs) -> None:
	"""Run fn in a background thread, logging errors instead of raising.

	Transitional shim for Django-side callers (Django's tasks framework has no
	backgroundable backend without a worker). Endpoints migrated to Litestar
	should use its native response BackgroundTask instead.
	"""

	def run():
		try:
			fn(*args, **kwargs)
		except Exception:
			logger.exception('Background task %s failed', fn.__name__)
		finally:
			close_old_connections()

	_executor.submit(run)


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


def resolve_expired_work(work_id: int):
	"""Delist a work once its moderation window has elapsed."""
	from otodb.account.models import Account
	from otodb.models import MediaWork
	from otodb.models.enums import Status
	from otodb.moderation import resolve_work

	try:
		work = MediaWork.objects.get(id=work_id)
	except MediaWork.DoesNotExist:
		return

	if work.status == Status.PENDING:
		resolve_work(work, by=Account.get_system(), reason='Auto-expired')


def resolve_expired_flag(event_id: int):
	"""Delist a flagged work whose pending flag was never actioned in time."""
	from otodb.account.models import Account
	from otodb.models import ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType
	from otodb.moderation import resolve_work

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


def resolve_expired_appeal(event_id: int):
	"""Re-delist a work whose pending appeal was never actioned in time."""
	from otodb.account.models import Account
	from otodb.models import ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType
	from otodb.moderation import resolve_work

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


def resolve_expired_source(source_id: int):
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


def prune_expired() -> int:
	"""Resolve every pending, flagged, and appealed work and pending source
	whose moderation window has elapsed.
	"""
	from otodb.models import MediaWork, ModerationEvent
	from otodb.models.enums import FlagStatus, ModerationEventType, Status
	from otodb.models.work_source import WorkSource

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	total = 0

	for work_id in MediaWork.objects.filter(
		status=Status.PENDING, created_at__lt=cutoff
	).values_list('id', flat=True):
		resolve_expired_work(work_id)
		total += 1

	for event_id in ModerationEvent.objects.filter(
		event_type=ModerationEventType.FLAG,
		status=FlagStatus.PENDING,
		date__lt=cutoff,
	).values_list('id', flat=True):
		resolve_expired_flag(event_id)
		total += 1

	for event_id in ModerationEvent.objects.filter(
		event_type=ModerationEventType.APPEAL,
		status=FlagStatus.PENDING,
		date__lt=cutoff,
	).values_list('id', flat=True):
		resolve_expired_appeal(event_id)
		total += 1

	for source_id in WorkSource.objects.filter(
		is_pending=True, created_at__lt=cutoff
	).values_list('id', flat=True):
		resolve_expired_source(source_id)
		total += 1

	return total
