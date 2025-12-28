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


# Module-level migration functions that can be properly serialized
def update_revision_renames(apps, schema_editor, app_label, model_name, field_renames):
	"""Update RevisionChange records for renamed fields."""
	RevisionChange = apps.get_model('otodb', 'RevisionChange')
	ContentType = apps.get_model('contenttypes', 'ContentType')

	try:
		content_type = ContentType.objects.get(
			app_label=app_label, model=model_name.lower()
		)
	except ContentType.DoesNotExist:
		return

	for old_name, new_name in field_renames.items():
		updated = RevisionChange.objects.filter(
			target_type=content_type, target_column=old_name
		).update(target_column=new_name)

		if updated > 0:
			print(
				f'  Updated {updated} RevisionChange records: {old_name} -> {new_name}'
			)


def reverse_revision_renames(apps, schema_editor, app_label, model_name, field_renames):
	"""Reverse RevisionChange records for renamed fields."""
	RevisionChange = apps.get_model('otodb', 'RevisionChange')
	ContentType = apps.get_model('contenttypes', 'ContentType')

	try:
		content_type = ContentType.objects.get(
			app_label=app_label, model=model_name.lower()
		)
	except ContentType.DoesNotExist:
		return

	# Reverse the renames
	for old_name, new_name in field_renames.items():
		RevisionChange.objects.filter(
			target_type=content_type, target_column=new_name
		).update(target_column=old_name)


def remove_revision_fields(apps, schema_editor, app_label, model_name, field_removes):
	"""Delete RevisionChange records for removed fields."""
	RevisionChange = apps.get_model('otodb', 'RevisionChange')
	ContentType = apps.get_model('contenttypes', 'ContentType')

	try:
		content_type = ContentType.objects.get(
			app_label=app_label, model=model_name.lower()
		)
	except ContentType.DoesNotExist:
		return

	for field_name in field_removes:
		deleted_count = RevisionChange.objects.filter(
			target_type=content_type, target_column=field_name
		).delete()[0]

		if deleted_count > 0:
			print(
				f'  Deleted {deleted_count} RevisionChange records for removed field: {field_name}'
			)


class RevisionTrackingOperation(migrations.RunPython):
	"""
	Custom migration operation that stores revision tracking metadata.
	This allows us to serialize the operation with the necessary data.
	"""

	def __init__(self, operation_type, app_label, model_name, field_data):
		self.operation_type = operation_type
		self.app_label = app_label
		self.model_name = model_name
		self.field_data = field_data

		if operation_type == 'rename':

			def code(apps, schema_editor):
				return update_revision_renames(
					apps, schema_editor, app_label, model_name, field_data
				)

			def reverse_code(apps, schema_editor):
				return reverse_revision_renames(
					apps, schema_editor, app_label, model_name, field_data
				)
		elif operation_type == 'remove':

			def code(apps, schema_editor):
				return remove_revision_fields(
					apps, schema_editor, app_label, model_name, field_data
				)

			reverse_code = migrations.RunPython.noop
		else:
			raise ValueError(f'Unknown operation type: {operation_type}')

		super().__init__(code=code, reverse_code=reverse_code)

	def deconstruct(self):
		"""
		Return a serializable representation of this operation.
		Django calls this when writing the migration file.
		"""
		kwargs = {
			'operation_type': self.operation_type,
			'app_label': self.app_label,
			'model_name': self.model_name,
			'field_data': self.field_data,
		}
		return (self.__class__.__qualname__, [], kwargs)


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
				if hasattr(model, '_revision_meta'):
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

					# Only track if either old or new field name is in revision_tracked_fields
					tracked_fields = model._revision_meta.tracked_fields
					if old_name in tracked_fields or new_name in tracked_fields:
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
					if field_name in model._revision_meta.tracked_fields:
						if model_name not in models_to_update:
							models_to_update[model_name] = {
								'renames': {},
								'removes': [],
							}
						models_to_update[model_name]['removes'].append(field_name)

		# Generate data migration operations
		for model_name, changes in models_to_update.items():
			if changes['renames'] or changes['removes']:
				if changes['renames']:
					# Add rename operation
					migration.operations.append(
						RevisionTrackingOperation(
							operation_type='rename',
							app_label=app_label,
							model_name=model_name,
							field_data=changes['renames'],
						)
					)

				if changes['removes']:
					# Add remove operation
					migration.operations.append(
						RevisionTrackingOperation(
							operation_type='remove',
							app_label=app_label,
							model_name=model_name,
							field_data=changes['removes'],
						)
					)

				# Print success message
				self.stdout.write(
					self.style.SUCCESS(
						f'\nAdded data migration for {model_name} revision tracking updates'
					)
				)

				# Print detailed info
				if changes['renames']:
					for old_name, new_name in changes['renames'].items():
						self.stdout.write(f'  - Rename: {old_name} -> {new_name}')
				if changes['removes']:
					for field_name in changes['removes']:
						self.stdout.write(f'  - Remove: {field_name}')
