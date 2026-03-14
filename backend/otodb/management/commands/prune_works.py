from django.core.management.base import BaseCommand

from otodb.tasks import prune_all_expired


class Command(BaseCommand):
	help = (
		'Resolve all expired pending, flagged, and appealed works and pending sources'
	)

	def handle(self, *args, **options):
		total = prune_all_expired()
		self.stdout.write(f'Done. Total resolved: {total}')
