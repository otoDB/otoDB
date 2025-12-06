"""
Refresh the tag search materialized view.

This command refreshes the PostgreSQL materialized view used for optimized tag search.
The materialized view pre-computes tag instance counts, language preferences, and alias data
to enable fast single-query tag searches.

This should be run periodically to keep search results fresh.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
	help = 'Refresh the tag search materialized view (PostgreSQL only)'

	def add_arguments(self, parser):
		parser.add_argument(
			'--no-concurrent',
			action='store_true',
			help='Disable concurrent refresh (faster but locks table)',
		)

	def handle(self, *args, **options):
		if connection.vendor != 'postgresql':
			self.stdout.write(
				self.style.WARNING(
					'Materialized views are only supported on PostgreSQL. '
					'This command is not needed for SQLite development environments.'
				)
			)
			return

		try:
			concurrent = '' if options['no_concurrent'] else 'CONCURRENTLY'

			with connection.cursor() as cursor:
				self.stdout.write(f'Refreshing materialized view {concurrent}...')
				cursor.execute(
					f'REFRESH MATERIALIZED VIEW {concurrent} otodb_tagwork_search_mv'
				)

			self.stdout.write(
				self.style.SUCCESS(
					'Successfully refreshed tag search materialized view'
				)
			)
		except Exception as e:
			self.stdout.write(
				self.style.ERROR(f'Failed to refresh materialized view: {e}')
			)
			raise
