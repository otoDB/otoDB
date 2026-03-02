from django.tasks import task
from django_scheduled_tasks import cron_task
from django.utils import timezone
from django.conf import settings


@cron_task(cron_schedule='0 * * * *')
@task
def prune_expired_works():
	"""Resolve all expired pending/flagged/appealed works."""
	from otodb.models import MediaWork
	from otodb.models.media import WorkFlag, WorkAppeal
	from otodb.models.enums import FlagStatus, Status
	from otodb.api.work import resolve_work

	cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
	total = 0

	# Expired pending works
	for work in MediaWork.objects.filter(status=Status.PENDING, created_at__lt=cutoff):
		resolve_work(work)
		total += 1

	# Expired flags
	expired_flag_work_ids = (
		WorkFlag.objects.filter(status=FlagStatus.PENDING, date__lt=cutoff)
		.values_list('work_id', flat=True)
		.distinct()
	)
	for work in MediaWork.objects.filter(id__in=expired_flag_work_ids):
		resolve_work(work)
		total += 1

	# Expired appeals
	expired_appeal_work_ids = (
		WorkAppeal.objects.filter(status=FlagStatus.PENDING, date__lt=cutoff)
		.values_list('work_id', flat=True)
		.distinct()
	)
	for work in MediaWork.objects.filter(id__in=expired_appeal_work_ids):
		resolve_work(work)
		total += 1

	# Expired pending sources (auto-reject)
	from otodb.models.work_source import WorkSource, WorkSourceRejection
	from otodb.account.models import Account

	expired_sources = WorkSource.objects.filter(is_pending=True, created_at__lt=cutoff)
	for src in expired_sources:
		if not hasattr(src, 'rejection'):
			WorkSourceRejection.objects.create(
				source=src,
				reason='Expired',
				by=Account.objects.filter(level=Account.Levels.OWNER).first(),
			)
		src.is_pending = False
		src.save(update_fields=['is_pending'])
		total += 1

	return total
