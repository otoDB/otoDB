from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from otodb.models import MediaWork, ModerationEvent
from otodb.models.enums import FlagStatus, ModerationEventType, Status
from otodb.models.work_source import WorkSource
from otodb.tasks import (
	resolve_expired_work,
	resolve_expired_flag,
	resolve_expired_appeal,
	resolve_expired_source_task,
)


class Command(BaseCommand):
	help = (
		'Resolve all expired pending, flagged, and appealed works and pending sources'
	)

	def handle(self, *args, **options):
		cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
		total = 0

		for work_id in MediaWork.objects.filter(
			status=Status.PENDING, created_at__lt=cutoff
		).values_list('id', flat=True):
			resolve_expired_work.call(work_id)
			total += 1

		for event_id in ModerationEvent.objects.filter(
			event_type=ModerationEventType.FLAG,
			status=FlagStatus.PENDING,
			date__lt=cutoff,
		).values_list('id', flat=True):
			resolve_expired_flag.call(event_id)
			total += 1

		for event_id in ModerationEvent.objects.filter(
			event_type=ModerationEventType.APPEAL,
			status=FlagStatus.PENDING,
			date__lt=cutoff,
		).values_list('id', flat=True):
			resolve_expired_appeal.call(event_id)
			total += 1

		for source_id in WorkSource.objects.filter(
			is_pending=True, created_at__lt=cutoff
		).values_list('id', flat=True):
			resolve_expired_source_task.call(source_id)
			total += 1

		self.stdout.write(f'Done. Total resolved: {total}')
