"""
Restore comments from merged works to their final destination.

When works are merged, from_work.moved_to is set to to_work,
but comments remain attached to from_work.pk. This command
follows the moved_to chain and updates comments accordingly.
"""

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django_comments_xtd.models import XtdComment

from otodb.models.media import MediaWork


class Command(BaseCommand):
	help = 'Restore comments from merged works to their current destination'

	def add_arguments(self, parser):
		parser.add_argument(
			'--dry-run',
			action='store_true',
			help='Show what would be migrated without making changes',
		)

	def handle(self, *args, **options):
		dry_run = options['dry_run']

		self.stdout.write('Starting comment restoration...')

		if dry_run:
			self.stdout.write(
				self.style.WARNING('DRY RUN MODE - No changes will be made')
			)

		try:
			mediawork_ct = ContentType.objects.get_for_model(MediaWork)
		except ContentType.DoesNotExist:
			self.stdout.write(self.style.ERROR('ContentType for MediaWork not found'))
			return

		merged_works = MediaWork.objects.filter(moved_to__isnull=False)
		total_merged = merged_works.count()

		self.stdout.write(f'Found {total_merged} merged works to check')

		migration_count = 0
		works_processed = 0

		for merged_work in merged_works:
			current_work = merged_work
			final_work = merged_work.moved_to
			visited = {current_work.pk}

			while final_work and final_work.moved_to and final_work.pk not in visited:
				visited.add(final_work.pk)
				final_work = final_work.moved_to

			if final_work and final_work.pk != merged_work.pk:
				comment_count = XtdComment.objects.filter(
					content_type=mediawork_ct, object_pk=str(merged_work.pk)
				).count()

				if comment_count > 0:
					if dry_run:
						self.stdout.write(
							f'  Would migrate {comment_count} comment(s) from work {merged_work.pk} to {final_work.pk}'
						)
					else:
						updated = XtdComment.objects.filter(
							content_type=mediawork_ct, object_pk=str(merged_work.pk)
						).update(object_pk=str(final_work.pk))

						self.stdout.write(
							f'  Migrated {updated} comment(s) from work {merged_work.pk} to {final_work.pk}'
						)

					migration_count += comment_count

			works_processed += 1

		self.stdout.write(self.style.SUCCESS('\nRestoration complete'))
		self.stdout.write(f'Processed {works_processed} merged works')
		self.stdout.write(
			f'Total comments {"would be" if dry_run else ""} migrated: {migration_count}'
		)

		if dry_run:
			self.stdout.write(
				self.style.WARNING('This was a dry run - no actual changes were made')
			)
