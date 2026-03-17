import logging

from django.db import transaction
from django.tasks import task
from django.conf import settings

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


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


def enqueue_deferred(task_func, *args):
	"""Enqueue a task to run after OTODB_MODERATION_PERIOD, via transaction.on_commit.

	Silently skips if the backend doesn't support defer (e.g. ImmediateBackend in dev).
	"""
	from django.tasks import default_task_backend

	if not default_task_backend.supports_defer:
		return

	def _enqueue():
		task_func.using(run_after=settings.OTODB_MODERATION_PERIOD).enqueue(*args)

	transaction.on_commit(_enqueue)


def reject_expired_source(src):
	"""Reject an expired pending source by unbinding it from its work."""
	from otodb.models.moderation import ModAction
	from otodb.models.enums import ModerationAction
	from otodb.account.models import Account

	src.media = None
	src.is_pending = False
	src.save(update_fields=['media', 'is_pending'])

	system_user = Account.objects.filter(level=Account.Levels.OWNER).first()
	if system_user:
		ModAction.objects.create(
			source=src,
			category=ModerationAction.SOURCE_REJECTED,
			by=system_user,
			description='Auto-expired',
		)


def prune_all_expired():
	"""Bulk resolve all expired pending items. Used by the management command."""
	from django.utils import timezone
	from otodb.models import MediaWork
	from otodb.models.moderation import WorkFlag, WorkAppeal
	from otodb.models.enums import FlagStatus, Status
	from otodb.models.work_source import WorkSource
	from otodb.api.work import resolve_work

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	total = 0

	for work in MediaWork.objects.filter(status=Status.PENDING, created_at__lt=cutoff):
		resolve_work(work)
		total += 1

	expired_flag_work_ids = (
		WorkFlag.objects.filter(status=FlagStatus.PENDING, date__lt=cutoff)
		.values_list('work_id', flat=True)
		.distinct()
	)
	for work in MediaWork.objects.filter(id__in=expired_flag_work_ids):
		resolve_work(work)
		total += 1

	expired_appeal_work_ids = (
		WorkAppeal.objects.filter(status=FlagStatus.PENDING, date__lt=cutoff)
		.values_list('work_id', flat=True)
		.distinct()
	)
	for work in MediaWork.objects.filter(id__in=expired_appeal_work_ids):
		resolve_work(work)
		total += 1

	for src in WorkSource.objects.filter(is_pending=True, created_at__lt=cutoff):
		reject_expired_source(src)
		total += 1

	return total


@task
def resolve_expired_work(work_id: int):
	"""Resolve a single pending work if it's still pending and past the moderation period."""
	from django.utils import timezone
	from otodb.models import MediaWork, ModAction
	from otodb.models.enums import Status, ModerationAction
	from otodb.api.work import resolve_work
	from otodb.account.models import Account

	try:
		work = MediaWork.objects.get(id=work_id)
	except MediaWork.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if work.status == Status.PENDING and work.created_at < cutoff:
		resolve_work(work)
		system_user = Account.objects.filter(level=Account.Levels.OWNER).first()
		if system_user:
			ModAction.objects.create(
				work=work,
				category=ModerationAction.WORK_DELISTED,
				by=system_user,
				description='Auto-expired',
			)


@task
def resolve_expired_flag(flag_id: int):
	"""Resolve a work with an expired pending flag."""
	from django.utils import timezone
	from otodb.models.moderation import WorkFlag
	from otodb.models.enums import FlagStatus
	from otodb.api.work import resolve_work

	try:
		flag = WorkFlag.objects.select_related('work').get(id=flag_id)
	except WorkFlag.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if flag.status == FlagStatus.PENDING and flag.date < cutoff:
		resolve_work(flag.work)


@task
def resolve_expired_appeal(appeal_id: int):
	"""Resolve a work with an expired pending appeal."""
	from django.utils import timezone
	from otodb.models.moderation import WorkAppeal
	from otodb.models.enums import FlagStatus
	from otodb.api.work import resolve_work

	try:
		appeal = WorkAppeal.objects.select_related('work').get(id=appeal_id)
	except WorkAppeal.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if appeal.status == FlagStatus.PENDING and appeal.date < cutoff:
		resolve_work(appeal.work)


@task
def resolve_expired_source_task(source_id: int):
	"""Auto-reject an expired pending source."""
	from django.utils import timezone
	from otodb.models.work_source import WorkSource

	try:
		src = WorkSource.objects.get(id=source_id)
	except WorkSource.DoesNotExist:
		return

	if not src.is_pending:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if src.created_at < cutoff:
		reject_expired_source(src)
