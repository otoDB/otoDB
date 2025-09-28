"""
Migrates existing thumbnails from old MediaWork._thumbnail field
to CDN via WorkSource.thumbnail_url.

1. Downloads thumbnails from old MediaWork._thumbnail URLs
2. Uploads them to CDN via WorkSource.save_thumbnail()
3. Sets MediaWork.thumbnail_source to appropriate WorkSource
4. Clears MediaWork._thumbnail field
"""

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from otodb.models.media import MediaWork
from otodb.models.enums import MimeType
from otodb.storage_manager import storage_manager


class Command(BaseCommand):
	help = 'Migrate existing thumbnails from MediaWork._thumbnail to CDN via WorkSource'

	def add_arguments(self, parser):
		parser.add_argument(
			'--dry-run',
			action='store_true',
		)
		parser.add_argument(
			'--batch-size',
			type=int,
			default=50,
			help='Number of works to process in each batch (default: 50)',
		)
		parser.add_argument(
			'--resume-from',
			type=int,
			help='Resume from specific MediaWork ID',
		)
		parser.add_argument(
			'--work-id',
			type=int,
			help='Process only specific MediaWork ID',
		)

	def handle(self, *args, **options):
		dry_run = options['dry_run']
		batch_size = options['batch_size']
		resume_from = options['resume_from']
		work_id = options['work_id']

		self.stdout.write(self.style.SUCCESS('Starting thumbnail migration...'))
		self.stdout.write(f'CDN enabled: {storage_manager.cdn_enabled}')

		if not storage_manager.cdn_enabled:
			raise CommandError(
				'CDN is not configured. Please check environment variables.'
			)

		query = MediaWork.active_objects.filter(_thumbnail__isnull=False)

		if work_id:
			query = query.filter(pk=work_id)
		elif resume_from:
			query = query.filter(pk__gte=resume_from)

		total_works = query.count()
		self.stdout.write(f'Found {total_works} works with thumbnails to migrate')

		if dry_run:
			self.stdout.write(
				self.style.WARNING('DRY RUN MODE - No changes will be made')
			)

		processed = 0
		success_count = 0
		error_count = 0

		for offset in range(0, total_works, batch_size):
			batch = query[offset : offset + batch_size]

			self.stdout.write(
				f'\nProcessing batch {offset // batch_size + 1} '
				f'({offset + 1}-{min(offset + batch_size, total_works)} of {total_works})'
			)

			for work in batch:
				try:
					success = self.migrate(work, dry_run)
					if success:
						success_count += 1
					else:
						error_count += 1
				except Exception as e:
					self.stdout.write(
						self.style.ERROR(
							f'Unexpected error processing Work {work.pk}: {e}'
						)
					)
					error_count += 1

				processed += 1

			self.stdout.write(
				f'Progress: {processed}/{total_works} '
				f'({success_count} success, {error_count} errors)'
			)

		self.stdout.write(self.style.SUCCESS('\nMigration complete!'))
		self.stdout.write(f'Results: {success_count} successful, {error_count} errors')

		if dry_run:
			self.stdout.write(
				self.style.WARNING('This was a dry run - no actual changes were made')
			)

	def migrate(self, work: MediaWork, dry_run: bool = False) -> bool:
		"""Migrate all thumbnails of WorkSources for a single MediaWork."""
		if not work._thumbnail:
			self.stdout.write(f'Work {work.pk}: No thumbnail to migrate')
			return True

		self.stdout.write(f'Work {work.pk}: Migrating thumbnail {work._thumbnail}')

		work_sources = work.worksource_set.all()
		if not work_sources:
			self.stdout.write(f'  No WorkSources found for Work {work.pk}')
			return False
		for source in work_sources:
			if dry_run:
				self.stdout.write(
					f'  [DRY RUN] Would migrate to WorkSource {source.pk}'
				)
				return True

			if not source.thumbnail_mime:
				try:
					response = requests.get(
						work._thumbnail, allow_redirects=True, timeout=10
					)
					content_type = response.headers.get('Content-Type')
					source.thumbnail_mime = MimeType.from_str(content_type)

					if not source.thumbnail_mime:
						self.stdout.write(
							f'  Could not detect MIME type for {work._thumbnail}'
						)
						return False
				except Exception as e:
					self.stdout.write(f'  Error detecting MIME type: {e}')
					return False

				success = source.save_thumbnail()
				if not success:
					self.stdout.write(
						f'  Failed to upload thumbnail for WorkSource {source.pk}'
					)
					return False

				source.save(update_fields=['thumbnail_mime'])
				self.stdout.write(f'  Uploaded thumbnail for WorkSource {source.pk}')

		first_source = work_sources.first()
		with transaction.atomic():
			work.thumbnail_source = first_source  # type: ignore
			work._thumbnail = None
			work.save(update_fields=['thumbnail_source', '_thumbnail'])
			self.stdout.write(
				f'  Set thumbnail_source to WorkSource {work.thumbnail_source.pk}'
			)  # type: ignore

		return True
