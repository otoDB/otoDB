"""
Fix merge directions where higher ID works point to lower ID works.

When works are merged, they should always result in the work with the lowest ID
being preserved. This command finds cases where a work with a lower ID has been
marked as moved_to a work with a higher ID, and reverses the merge direction.
"""

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django_comments_xtd.models import XtdComment

from otodb.models.media import MediaWork
from otodb.models.pool import PoolItem
from otodb.models.relations import WorkRelation
from otodb.models.work_source import WorkSource


class Command(BaseCommand):
	help = 'Fix merge directions to ensure lowest ID works are always preserved'

	def add_arguments(self, parser):
		parser.add_argument(
			'--dry-run',
			action='store_true',
			help='Show what would be fixed without making changes',
		)

	def handle(self, *args, **options):
		dry_run = options['dry_run']

		self.stdout.write('Starting merge direction fixes...')

		if dry_run:
			self.stdout.write(
				self.style.WARNING('DRY RUN MODE - No changes will be made')
			)

		# Find all cases where a lower ID work points to a higher ID work
		incorrect_merges = MediaWork.objects.filter(
			moved_to__isnull=False
		).select_related('moved_to')

		issues_found = []
		for work in incorrect_merges:
			if work.pk < work.moved_to.pk:
				issues_found.append((work, work.moved_to))

		if not issues_found:
			self.stdout.write(
				self.style.SUCCESS('No incorrect merge directions found!')
			)
			return

		self.stdout.write(
			f'Found {len(issues_found)} incorrect merge direction(s) to fix\n'
		)

		for lower_id_work, higher_id_work in issues_found:
			self.stdout.write(
				f'Fixing: Work {lower_id_work.pk} (currently marked as moved) -> Work {higher_id_work.pk}'
			)
			self.stdout.write(
				f'  Should be: Work {higher_id_work.pk} -> Work {lower_id_work.pk}'
			)

			if not dry_run:
				self._fix_merge_direction(lower_id_work, higher_id_work)

		self.stdout.write(self.style.SUCCESS('\nMerge direction fixes complete'))
		self.stdout.write(
			f'Total issues {"would be" if dry_run else ""} fixed: {len(issues_found)}'
		)

		if dry_run:
			self.stdout.write(
				self.style.WARNING('This was a dry run - no actual changes were made')
			)

	@transaction.atomic
	def _fix_merge_direction(self, lower_id_work, higher_id_work):
		"""
		Reverse the merge direction so that higher_id_work points to lower_id_work.

		This involves:
		1. Moving all sources from higher_id_work to lower_id_work
		2. Moving all pool items from higher_id_work to lower_id_work
		3. Updating all relations involving higher_id_work to use lower_id_work
		4. Moving all comments from higher_id_work to lower_id_work
		5. Clearing lower_id_work's moved_to pointer
		6. Setting higher_id_work's moved_to to lower_id_work
		"""
		self.stdout.write('  Reversing merge direction...')

		# Move all sources from higher_id_work to lower_id_work
		sources_moved = WorkSource.objects.filter(media=higher_id_work).update(
			media=lower_id_work
		)
		self.stdout.write(
			f'    Moved {sources_moved} source(s) from work {higher_id_work.pk} to {lower_id_work.pk}'
		)

		# Move pool items
		pool_items_moved = PoolItem.objects.filter(work=higher_id_work).update(
			work=lower_id_work
		)
		if pool_items_moved:
			self.stdout.write(f'    Moved {pool_items_moved} pool item(s)')

		# Fix relations where higher_id_work is side A
		relations_updated = 0
		for relation in WorkRelation.objects.filter(A=higher_id_work):
			if relation.B.pk == lower_id_work.pk:
				relation.delete()
			else:
				relation.A = lower_id_work
				relation.save()
				relations_updated += 1

		# Fix relations where higher_id_work is side B
		for relation in WorkRelation.objects.filter(B=higher_id_work):
			if relation.A.pk == lower_id_work.pk:
				relation.delete()
			else:
				relation.B = lower_id_work
				relation.save()
				relations_updated += 1

		if relations_updated:
			self.stdout.write(f'    Updated {relations_updated} relation(s)')

		# Move comments
		mediawork_ct = ContentType.objects.get_for_model(MediaWork)
		comments_moved = XtdComment.objects.filter(
			content_type=mediawork_ct, object_pk=str(higher_id_work.pk)
		).update(object_pk=str(lower_id_work.pk))
		if comments_moved:
			self.stdout.write(f'    Moved {comments_moved} comment(s)')

		# Update moved_to pointers
		lower_id_work.moved_to = None
		lower_id_work.save()

		higher_id_work.moved_to = lower_id_work
		higher_id_work.save()

		self.stdout.write(
			self.style.SUCCESS(
				f'    ✓ Fixed: Work {higher_id_work.pk} now points to work {lower_id_work.pk}'
			)
		)
