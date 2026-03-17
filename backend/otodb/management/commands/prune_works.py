from django.conf import settings
from django.core.management.base import BaseCommand

from django.utils import timezone
from otodb.models import MediaWork
from otodb.models.moderation import WorkFlag, WorkAppeal
from otodb.models.enums import FlagStatus, Status
from otodb.models.work_source import WorkSource
from otodb.models.moderation import ModAction
from otodb.models.enums import ModerationAction
from otodb.account.models import Account

# TODO: probably shouldn't import from API here -- refactor
from otodb.api.work import resolve_work


class Command(BaseCommand):
	help = (
		'Resolve all expired pending, flagged, and appealed works and pending sources'
	)

	def handle(self, *args, **options):
		cutoff = timezone.now() - settings.OTODB_MODERATION_PERIOD
		total = 0

		for work in MediaWork.objects.filter(
			status=Status.PENDING, created_at__lt=cutoff
		):
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
			# TODO: comes from _reject_expired_source -- refactor
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
			total += 1

		self.stdout.write(f'Done. Total resolved: {total}')
