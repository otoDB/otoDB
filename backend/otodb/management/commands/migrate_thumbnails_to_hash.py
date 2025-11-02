"""
Migrates existing thumbnails from ID-based paths to hash-based paths.

1. Reads existing thumbnails from old ID-based paths: /t/source/{id%100}/{id}.{ext}
2. Calculates SHA256 hash of the file content
3. Saves to new hash-based paths: /t/{hash[:2]}/{hash[2:4]}/{hash}.{ext}
4. Updates WorkSource.thumbnail_hash in database
5. Deletes old files after successful migration (optional)
"""

import hashlib
from django.core.management.base import BaseCommand
from django.db import transaction

from otodb.models.work_source import WorkSource
from otodb.models.enums import MimeType
from otodb.storage_manager import storage_manager


class Command(BaseCommand):
	help = 'Migrate existing thumbnails from ID-based paths to hash-based paths'

	def add_arguments(self, parser):
		parser.add_argument(
			'--dry-run',
			action='store_true',
			help='Show what would be done without making changes',
		)
		parser.add_argument(
			'--batch-size',
			type=int,
			default=50,
			help='Number of sources to process in each batch (default: 50)',
		)
		parser.add_argument(
			'--resume-from',
			type=int,
			help='Resume from specific WorkSource ID',
		)
		parser.add_argument(
			'--source-id',
			type=int,
			help='Process only specific WorkSource ID',
		)
		parser.add_argument(
			'--keep-old-files',
			action='store_true',
			help='Keep old ID-based files after migration (default: delete)',
		)

	def handle(self, *args, **options):
		dry_run = options['dry_run']
		batch_size = options['batch_size']
		resume_from = options['resume_from']
		source_id = options['source_id']
		keep_old_files = options['keep_old_files']

		self.stdout.write(self.style.SUCCESS('Starting thumbnail hash migration...'))
		self.stdout.write(f'CDN enabled: {storage_manager.cdn_enabled}')
		self.stdout.write(
			f'Storage: {"CDN" if storage_manager.cdn_enabled else "Local filesystem"}'
		)

		# Query WorkSources that have thumbnail_mime but no thumbnail_hash yet
		query = WorkSource.objects.filter(
			thumbnail_mime__isnull=False, thumbnail_hash__isnull=True
		)

		if source_id:
			query = query.filter(pk=source_id)
		elif resume_from:
			query = query.filter(pk__gte=resume_from)

		total_sources = query.count()
		self.stdout.write(f'Found {total_sources} sources with thumbnails to migrate')

		if dry_run:
			self.stdout.write(
				self.style.WARNING('DRY RUN MODE - No changes will be made')
			)

		processed = 0
		success_count = 0
		error_count = 0
		deduplicated_count = 0

		for offset in range(0, total_sources, batch_size):
			batch = query[offset : offset + batch_size]

			self.stdout.write(
				f'\nProcessing batch {offset // batch_size + 1} '
				f'({offset + 1}-{min(offset + batch_size, total_sources)} of {total_sources})'
			)

			for source in batch:
				try:
					result = self.migrate_source(source, dry_run, keep_old_files)
					if result == 'success':
						success_count += 1
					elif result == 'deduplicated':
						deduplicated_count += 1
					else:
						error_count += 1
				except Exception as e:
					self.stdout.write(
						self.style.ERROR(
							f'Unexpected error processing WorkSource {source.pk}: {e}'
						)
					)
					error_count += 1

				processed += 1

			self.stdout.write(
				f'Progress: {processed}/{total_sources} '
				f'({success_count} migrated, {deduplicated_count} deduplicated, {error_count} errors)'
			)

		self.stdout.write(self.style.SUCCESS('\nMigration complete!'))
		self.stdout.write(
			f'Results: {success_count} migrated, {deduplicated_count} deduplicated, {error_count} errors'
		)

		if dry_run:
			self.stdout.write(
				self.style.WARNING('This was a dry run - no actual changes were made')
			)

	def get_old_thumbnail_path(self, source: WorkSource) -> str:
		"""Generate the old ID-based thumbnail path."""
		ext = MimeType.extension(source.thumbnail_mime)
		return f'/t/source/{str(source.pk).zfill(2)[-2:]}/{source.pk}.{ext}'

	def migrate_source(
		self, source: WorkSource, dry_run: bool = False, keep_old_files: bool = False
	) -> str:
		"""
		Migrate a single WorkSource thumbnail from ID-based to hash-based path.

		Returns:
			'success' - Successfully migrated
			'deduplicated' - File already exists at hash path (deduplicated)
			'error' - Failed to migrate
		"""
		if not source.thumbnail_mime:
			self.stdout.write(f'WorkSource {source.pk}: No thumbnail_mime set')
			return 'error'

		old_path = self.get_old_thumbnail_path(source)
		self.stdout.write(f'WorkSource {source.pk}: Processing {old_path}')

		if dry_run:
			self.stdout.write(f'  [DRY RUN] Would read file from {old_path}')
			self.stdout.write('  [DRY RUN] Would calculate SHA256 hash')
			self.stdout.write('  [DRY RUN] Would save to hash-based path')
			return 'success'

		# Try to read the file from old path
		try:
			file_content = storage_manager.read(old_path)
			if file_content is None:
				self.stdout.write(
					self.style.WARNING(
						f'  File not found at {old_path}, skipping (may have been migrated already or never existed)'
					)
				)
				return 'error'
		except Exception as e:
			self.stdout.write(
				self.style.ERROR(f'  Error reading file from {old_path}: {e}')
			)
			return 'error'

		# Calculate SHA256 hash
		try:
			content_hash = hashlib.sha256(file_content).hexdigest()
			source.thumbnail_hash = content_hash
			self.stdout.write(f'  Calculated hash: {content_hash[:16]}...')
		except Exception as e:
			self.stdout.write(self.style.ERROR(f'  Error calculating hash: {e}'))
			return 'error'

		# Get new hash-based path
		ext = MimeType.extension(source.thumbnail_mime)
		new_path = f'/t/{content_hash[:2]}/{content_hash[2:4]}/{content_hash}.{ext}'

		# Check if file already exists at hash path (deduplication)
		if storage_manager.exists(new_path):
			self.stdout.write(
				self.style.SUCCESS(
					f'  File already exists at {new_path} (deduplicated)'
				)
			)

			# Update database with hash
			try:
				with transaction.atomic():
					source.save(update_fields=['thumbnail_hash'])
				self.stdout.write('  Updated thumbnail_hash in database')
			except Exception as e:
				self.stdout.write(self.style.ERROR(f'  Error updating database: {e}'))
				return 'error'

			# Delete old file if requested
			if not keep_old_files:
				try:
					storage_manager.delete(old_path)
					self.stdout.write(f'  Deleted old file at {old_path}')
				except Exception as e:
					self.stdout.write(
						self.style.WARNING(f'  Could not delete old file: {e}')
					)

			return 'deduplicated'

		# Save file to new hash-based path
		try:
			saved_path = storage_manager.save(file_content, new_path)
			if not saved_path:
				self.stdout.write(
					self.style.ERROR(f'  Failed to save file to {new_path}')
				)
				return 'error'
			self.stdout.write(f'  Saved file to {new_path}')
		except Exception as e:
			self.stdout.write(self.style.ERROR(f'  Error saving file: {e}'))
			return 'error'

		# Update database with hash
		try:
			with transaction.atomic():
				source.save(update_fields=['thumbnail_hash'])
			self.stdout.write('  Updated thumbnail_hash in database')
		except Exception as e:
			self.stdout.write(self.style.ERROR(f'  Error updating database: {e}'))
			return 'error'

		# Delete old file if requested
		if not keep_old_files:
			try:
				storage_manager.delete(old_path)
				self.stdout.write(f'  Deleted old file at {old_path}')
			except Exception as e:
				self.stdout.write(
					self.style.WARNING(f'  Could not delete old file: {e}')
				)

		self.stdout.write(self.style.SUCCESS('  ✓ Successfully migrated'))
		return 'success'
