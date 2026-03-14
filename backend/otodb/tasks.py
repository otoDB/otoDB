from django.db import transaction
from django.tasks import task
from django.conf import settings


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
	"""Reject an expired pending source by creating a WorkSourceRejection."""
	from otodb.models.work_source import WorkSourceRejection
	from otodb.account.models import Account

	if not hasattr(src, 'rejection'):
		WorkSourceRejection.objects.create(
			source=src,
			reason='Expired',
			by=Account.objects.filter(level=Account.Levels.OWNER).first(),
		)
	src.is_pending = False
	src.save(update_fields=['is_pending'])


def prune_all_expired():
	"""Bulk resolve all expired pending items. Used by the management command."""
	from django.utils import timezone
	from otodb.models import MediaWork
	from otodb.models.media import WorkFlag, WorkAppeal
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
	from otodb.models import MediaWork
	from otodb.models.enums import Status
	from otodb.api.work import resolve_work

	try:
		work = MediaWork.objects.get(id=work_id)
	except MediaWork.DoesNotExist:
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if work.status == Status.PENDING and work.created_at < cutoff:
		resolve_work(work)


@task
def resolve_expired_flag(flag_id: int):
	"""Resolve a work with an expired pending flag."""
	from django.utils import timezone
	from otodb.models.media import WorkFlag
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
	from otodb.models.media import WorkAppeal
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

	if not src.is_pending or hasattr(src, 'rejection'):
		return

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	if src.created_at < cutoff:
		reject_expired_source(src)
