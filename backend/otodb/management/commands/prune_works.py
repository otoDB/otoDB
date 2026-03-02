from django.core.management.base import BaseCommand

from otodb.tasks import prune_expired_works


class Command(BaseCommand):
	help = 'Resolve expired pending, flagged, and appealed works'

	def handle(self, *args, **options):
		total = prune_expired_works()
		self.stdout.write(f'Done. Total resolved works: {total}')
