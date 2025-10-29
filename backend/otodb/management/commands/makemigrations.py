"""
Custom makemigrations command that automatically handles revision_tracked_fields updates.

This command extends Django's makemigrations to detect field renames/deletions in
RevisionTrackedModel subclasses and automatically generates data migrations to update
RevisionChange records in the database.

Usage:
    python manage.py makemigrations

When fields are renamed or removed from models with revision_tracked_fields, this command:
1. Detects the change
2. Automatically adds RunPython operations to update RevisionChange.target_column
3. Prints confirmation messages
"""

from django.core.management.commands.makemigrations import (
	Command as MakeMigrationsCommand,
)
from django.db import migrations
from django.apps import apps


class Command(MakeMigrationsCommand):
	"""
	Extended makemigrations that automatically handles revision_tracked_fields
	and generates data migrations for RevisionChange records.
	"""

	def write_migration_files(self, changes, *args, **kwargs):
		"""
		Override to inject revision history updates into migrations.
		"""
		# Process each app's migrations
		for app_label, app_migrations in changes.items():
			for migration in app_migrations:
				self._inject_revision_updates(app_label, migration)

		# Call parent to write the files
		return super().write_migration_files(changes, *args, **kwargs)

	def _inject_revision_updates(self, app_label, migration):
		"""
		Inject data migration operations to update RevisionChange records.
		"""
		# Track which models need revision_tracked_fields updates
		models_to_update = {}

		# Get all RevisionTrackedModel subclasses
		revision_tracked_models = {}
		try:
			for model in apps.get_app_config(app_label).get_models():
				if hasattr(model, 'revision_tracked_fields'):
					revision_tracked_models[model.__name__.lower()] = model
		except LookupError:
			pass

		for operation in migration.operations:
			# Handle field renames
			if isinstance(operation, migrations.RenameField):
				model_name_lower = operation.model_name.lower()
				if model_name_lower in revision_tracked_models:
					model = revision_tracked_models[model_name_lower]
					model_name = operation.model_name
					old_name = operation.old_name
					new_name = operation.new_name

					# Only track if this field is in revision_tracked_fields
					if old_name in getattr(model, 'revision_tracked_fields', []):
						if model_name not in models_to_update:
							models_to_update[model_name] = {
								'renames': {},
								'removes': [],
							}
						models_to_update[model_name]['renames'][old_name] = new_name

			# Handle field removals
			elif isinstance(operation, migrations.RemoveField):
				model_name_lower = operation.model_name.lower()
				if model_name_lower in revision_tracked_models:
					model = revision_tracked_models[model_name_lower]
					model_name = operation.model_name
					field_name = operation.name

					# Only track if this field is in revision_tracked_fields
					if field_name in getattr(model, 'revision_tracked_fields', []):
						if model_name not in models_to_update:
							models_to_update[model_name] = {
								'renames': {},
								'removes': [],
							}
						models_to_update[model_name]['removes'].append(field_name)

		# Generate data migration operations
		for model_name, changes in models_to_update.items():
			if changes['renames'] or changes['removes']:
				# Create the data migration function
				forward_func = self._create_data_migration_forward(
					app_label, model_name, changes
				)
				reverse_func = self._create_data_migration_reverse(
					app_label, model_name, changes
				)

				# Add RunPython operation
				migration.operations.append(
					migrations.RunPython(
						code=forward_func,
						reverse_code=reverse_func,
					)
				)

				# Print success message
				self.stdout.write(
					self.style.SUCCESS(
						f'\n✓ Added data migration for {model_name} revision tracking updates'
					)
				)

				# Print detailed info
				if changes['renames']:
					for old_name, new_name in changes['renames'].items():
						self.stdout.write(f'  - Rename: {old_name} → {new_name}')
				if changes['removes']:
					for field_name in changes['removes']:
						self.stdout.write(f'  - Remove: {field_name}')

	def _create_data_migration_forward(self, app_label, model_name, changes):
		"""
		Create forward data migration function to update RevisionChange records.
		"""
		renames = changes['renames']
		removes = changes['removes']

		def update_revision_changes(apps, schema_editor):
			"""Update RevisionChange records for field renames/removals."""
			RevisionChange = apps.get_model('otodb', 'RevisionChange')
			ContentType = apps.get_model('contenttypes', 'ContentType')

			# Get the content type for this model
			try:
				content_type = ContentType.objects.get(
					app_label=app_label, model=model_name.lower()
				)
			except ContentType.DoesNotExist:
				return

			# Handle renames
			for old_name, new_name in renames.items():
				updated = RevisionChange.objects.filter(
					target_type=content_type, target_column=old_name
				).update(target_column=new_name)

				if updated > 0:
					print(
						f'  Updated {updated} RevisionChange records: {old_name} → {new_name}'
					)

			# Handle removes (delete obsolete records)
			for field_name in removes:
				deleted_count = RevisionChange.objects.filter(
					target_type=content_type, target_column=field_name
				).delete()[0]

				if deleted_count > 0:
					print(
						f'  Deleted {deleted_count} RevisionChange records for removed field: {field_name}'
					)

		return update_revision_changes

	def _create_data_migration_reverse(self, app_label, model_name, changes):
		"""
		Create reverse data migration function.
		"""
		renames = changes['renames']

		def reverse_revision_changes(apps, schema_editor):
			"""Reverse the RevisionChange updates."""
			RevisionChange = apps.get_model('otodb', 'RevisionChange')
			ContentType = apps.get_model('contenttypes', 'ContentType')

			try:
				content_type = ContentType.objects.get(
					app_label=app_label, model=model_name.lower()
				)
			except ContentType.DoesNotExist:
				return

			# Reverse renames
			for old_name, new_name in renames.items():
				RevisionChange.objects.filter(
					target_type=content_type, target_column=new_name
				).update(target_column=old_name)

			# Note: Removed fields cannot be restored in reverse

		return reverse_revision_changes
