from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0114_migrate_threads_data'),
	]

	operations = [
		# Notifications no longer point at a thread directly (they point at a post).
		migrations.RemoveField(
			model_name='notification',
			name='post',
		),
		migrations.AddConstraint(
			model_name='notification',
			constraint=models.CheckConstraint(
				condition=models.Q(
					models.Q(
						('comment__isnull', True),
						('revision__isnull', False),
						('threadpost__isnull', True),
					),
					models.Q(
						('comment__isnull', False),
						('revision__isnull', True),
						('threadpost__isnull', True),
					),
					models.Q(
						('comment__isnull', True),
						('revision__isnull', True),
						('threadpost__isnull', False),
					),
					_connector='OR',
				),
				name='notification_union',
			),
		),
		# Thread title/category/lang edits are not tracked.
		migrations.RemoveField(model_name='thread', name='edited_at'),
		migrations.RemoveField(model_name='thread', name='edited_by'),
		# Opening bodies now live in ThreadPost num=1.
		migrations.DeleteModel(name='PostContent'),
	]
