"""Tests for custom makemigrations command with revision tracking."""

import pytest
from io import StringIO
from unittest.mock import Mock, patch
from django.db import migrations
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import OutputWrapper

from otodb.management.commands.makemigrations import (
	Command,
	RevisionTrackingOperation,
	update_revision_renames,
	reverse_revision_renames,
	remove_revision_fields,
)
from otodb.models import MediaWork, RevisionChange


@pytest.mark.django_db
class TestMakemigrationsCommand:
	"""Test the custom makemigrations command."""

	def test_command_imports(self):
		"""Test that the command class can be imported."""
		assert Command is not None
		assert hasattr(Command, 'write_migration_files')
		assert hasattr(Command, '_inject_revision_updates')

	def test_inject_revision_updates_with_rename(self, db):
		"""Test that RenameField operations are detected and handled."""
		command = Command()

		# Create a mock migration with a RenameField operation
		mock_migration = Mock()
		mock_migration.operations = [
			migrations.RenameField(
				model_name='mediawork', old_name='description', new_name='desc'
			)
		]

		# Mock the app config to return MediaWork as a tracked model
		with patch('otodb.management.commands.makemigrations.apps') as mock_apps:
			mock_config = Mock()
			mock_config.get_models.return_value = [MediaWork]
			mock_apps.get_app_config.return_value = mock_config

			# Call the injection method
			command._inject_revision_updates('otodb', mock_migration)

		# Verify a RevisionTrackingOperation was added
		assert len(mock_migration.operations) == 2
		assert isinstance(mock_migration.operations[1], RevisionTrackingOperation)
		assert mock_migration.operations[1].operation_type == 'rename'
		assert mock_migration.operations[1].field_data == {'description': 'desc'}

	def test_inject_revision_updates_with_remove(self, db):
		"""Test that RemoveField operations are detected and handled."""
		command = Command()

		# Create a mock migration with a RemoveField operation
		mock_migration = Mock()
		mock_migration.operations = [
			migrations.RemoveField(model_name='mediawork', name='description')
		]

		# Mock the app config
		with patch('otodb.management.commands.makemigrations.apps') as mock_apps:
			mock_config = Mock()
			mock_config.get_models.return_value = [MediaWork]
			mock_apps.get_app_config.return_value = mock_config

			command._inject_revision_updates('otodb', mock_migration)

		# Verify a RevisionTrackingOperation was added
		assert len(mock_migration.operations) == 2
		assert isinstance(mock_migration.operations[1], RevisionTrackingOperation)
		assert mock_migration.operations[1].operation_type == 'remove'
		assert mock_migration.operations[1].field_data == ['description']

	def test_inject_revision_updates_ignores_untracked_fields(self, db):
		"""Test that fields not in revision_tracked_fields are ignored."""
		command = Command()

		# Create a mock migration with a RenameField for an untracked field
		mock_migration = Mock()
		mock_migration.operations = [
			migrations.RenameField(
				model_name='mediawork',
				old_name='_thumbnail',  # This is not in revision_tracked_fields
				new_name='thumbnail_new',
			)
		]

		with patch('otodb.management.commands.makemigrations.apps') as mock_apps:
			mock_config = Mock()
			mock_config.get_models.return_value = [MediaWork]
			mock_apps.get_app_config.return_value = mock_config

			command._inject_revision_updates('otodb', mock_migration)

		# Verify NO RunPython operation was added
		assert len(mock_migration.operations) == 1

	def test_inject_revision_updates_ignores_non_tracked_models(self, db):
		"""Test that models without revision_tracked_fields are ignored."""
		command = Command()

		# Create a mock model without revision tracking
		MockModel = type('MockModel', (), {})

		mock_migration = Mock()
		mock_migration.operations = [
			migrations.RenameField(
				model_name='mockmodel', old_name='field1', new_name='field2'
			)
		]

		with patch('otodb.management.commands.makemigrations.apps') as mock_apps:
			mock_config = Mock()
			mock_config.get_models.return_value = [MockModel]
			mock_apps.get_app_config.return_value = mock_config

			command._inject_revision_updates('otodb', mock_migration)

		# Verify NO RunPython operation was added
		assert len(mock_migration.operations) == 1


@pytest.mark.django_db
class TestDataMigrationFunctions:
	"""Test the module-level data migration functions."""

	def test_update_revision_renames(
		self, test_work, test_revision, test_revision_change
	):
		"""Test that update_revision_renames updates RevisionChange records."""
		# Mock apps to return actual models
		mock_apps = Mock()
		mock_apps.get_model = Mock(
			side_effect=lambda app, model: {
				('otodb', 'RevisionChange'): RevisionChange,
				('contenttypes', 'ContentType'): ContentType,
			}[(app, model)]
		)

		# Run the function
		update_revision_renames(
			mock_apps, None, 'otodb', 'MediaWork', {'title': 'work_title'}
		)

		# Verify the RevisionChange was updated
		updated_change = RevisionChange.objects.get(pk=test_revision_change.pk)
		assert updated_change.target_column == 'work_title'

	def test_remove_revision_fields(
		self, test_work, test_revision, test_revision_change
	):
		"""Test that remove_revision_fields deletes RevisionChange records for removed fields."""
		# Mock apps
		mock_apps = Mock()
		mock_apps.get_model = Mock(
			side_effect=lambda app, model: {
				('otodb', 'RevisionChange'): RevisionChange,
				('contenttypes', 'ContentType'): ContentType,
			}[(app, model)]
		)

		# Run the function
		remove_revision_fields(mock_apps, None, 'otodb', 'MediaWork', ['title'])

		# Verify the RevisionChange was deleted
		assert not RevisionChange.objects.filter(pk=test_revision_change.pk).exists()

	def test_reverse_revision_renames(self, test_work, test_revision):
		"""Test that reverse_revision_renames restores original field names."""
		# Create a RevisionChange with the new name
		content_type = ContentType.objects.get_for_model(MediaWork)
		change = RevisionChange.objects.create(
			rev=test_revision,
			target_type=content_type,
			target_id=test_work.pk,
			target_column='work_title',  # New name
			target_value='Test Work',
		)

		# Mock apps
		mock_apps = Mock()
		mock_apps.get_model = Mock(
			side_effect=lambda app, model: {
				('otodb', 'RevisionChange'): RevisionChange,
				('contenttypes', 'ContentType'): ContentType,
			}[(app, model)]
		)

		# Run the reverse function
		reverse_revision_renames(
			mock_apps, None, 'otodb', 'MediaWork', {'title': 'work_title'}
		)

		# Verify the RevisionChange was reverted to old name
		updated_change = RevisionChange.objects.get(pk=change.pk)
		assert updated_change.target_column == 'title'

	def test_update_revision_renames_handles_missing_content_type(self, member):
		"""Test that update_revision_renames gracefully handles missing ContentType."""
		# Mock apps
		mock_apps = Mock()
		mock_apps.get_model = Mock(
			side_effect=lambda app, model: {
				('otodb', 'RevisionChange'): RevisionChange,
				('contenttypes', 'ContentType'): ContentType,
			}[(app, model)]
		)

		# Should not raise an exception
		update_revision_renames(
			mock_apps, None, 'otodb', 'NonExistentModel', {'title': 'work_title'}
		)

	def test_update_revision_renames_multiple_fields(self, test_work, test_revision):
		"""Test handling multiple field renames in a single call."""
		content_type = ContentType.objects.get_for_model(MediaWork)

		# Create multiple RevisionChange records
		change1 = RevisionChange.objects.create(
			rev=test_revision,
			target_type=content_type,
			target_id=test_work.pk,
			target_column='title',
			target_value='Test Work',
		)
		change2 = RevisionChange.objects.create(
			rev=test_revision,
			target_type=content_type,
			target_id=test_work.pk,
			target_column='description',
			target_value='Test Description',
		)

		# Mock apps
		mock_apps = Mock()
		mock_apps.get_model = Mock(
			side_effect=lambda app, model: {
				('otodb', 'RevisionChange'): RevisionChange,
				('contenttypes', 'ContentType'): ContentType,
			}[(app, model)]
		)

		# Run the function with multiple renames
		update_revision_renames(
			mock_apps,
			None,
			'otodb',
			'MediaWork',
			{'title': 'work_title', 'description': 'work_desc'},
		)

		# Verify both were updated
		updated1 = RevisionChange.objects.get(pk=change1.pk)
		updated2 = RevisionChange.objects.get(pk=change2.pk)
		assert updated1.target_column == 'work_title'
		assert updated2.target_column == 'work_desc'


@pytest.mark.django_db
class TestCommandIntegration:
	"""Integration tests for the full command workflow."""

	def test_write_migration_files_calls_inject(self):
		"""Test that write_migration_files calls _inject_revision_updates."""
		command = Command()

		# Mock the parent's write_migration_files
		with patch.object(
			Command.__bases__[0], 'write_migration_files', return_value=None
		) as mock_parent:
			with patch.object(command, '_inject_revision_updates') as mock_inject:
				# Create mock changes
				mock_migration = Mock()
				mock_migration.operations = []
				changes = {'otodb': [mock_migration]}

				# Call the method
				command.write_migration_files(changes)

				# Verify _inject_revision_updates was called
				mock_inject.assert_called_once_with('otodb', mock_migration)

				# Verify parent was called
				mock_parent.assert_called_once()

	def test_command_prints_success_messages(self, capsys):
		"""Test that the command prints success messages."""
		command = Command()
		command.stdout = OutputWrapper(StringIO())

		# Create a mock migration with a tracked field rename
		mock_migration = Mock()
		mock_migration.operations = [
			migrations.RenameField(
				model_name='mediawork', old_name='description', new_name='desc'
			)
		]

		with patch('otodb.management.commands.makemigrations.apps') as mock_apps:
			mock_config = Mock()
			mock_config.get_models.return_value = [MediaWork]
			mock_apps.get_app_config.return_value = mock_config

			command._inject_revision_updates('otodb', mock_migration)

		# Check that success message was written
		output = command.stdout.getvalue().lower()
		assert 'added data migration for mediawork' in output
		assert 'rename: description -> desc' in output
