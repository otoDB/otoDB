import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
		('otodb', '0113_alter_userpreference_setting'),
	]

	operations = [
		# Drop the old union constraint so post -> threadpost can be migrated freely.
		migrations.RemoveConstraint(
			model_name='notification',
			name='notification_union',
		),
		# Post is now Thread (renames table + content type; data preserved).
		migrations.RenameModel(old_name='Post', new_name='Thread'),
		migrations.AlterModelOptions(
			name='thread',
			options={'verbose_name': 'Thread', 'verbose_name_plural': 'Threads'},
		),
		# EntityLink.post -> EntityLink.thread.
		migrations.RemoveConstraint(
			model_name='entitylink',
			name='entitylink_unique_post',
		),
		migrations.RenameField(
			model_name='entitylink', old_name='post', new_name='thread'
		),
		migrations.AddConstraint(
			model_name='entitylink',
			constraint=models.UniqueConstraint(
				fields=('entity_type', 'entity_id', 'thread'),
				name='entitylink_unique_post',
			),
		),
		# New thread-level fields.
		migrations.AddField(
			model_name='thread',
			name='lang',
			field=models.IntegerField(
				choices=[
					(0, 'N/A'),
					(1, 'en'),
					(2, 'ja'),
					(3, 'zh-cn'),
					(4, 'ko'),
				],
				default=1,
			),
			preserve_default=False,
		),
		migrations.AddField(
			model_name='thread',
			name='created_at',
			field=models.DateTimeField(default=django.utils.timezone.now),
		),
		migrations.AddField(
			model_name='thread',
			name='is_removed',
			field=models.BooleanField(db_index=True, default=False),
		),
		# The flat list of posts that make up a thread (OP is num=1).
		migrations.CreateModel(
			name='ThreadPost',
			fields=[
				(
					'id',
					models.BigAutoField(
						auto_created=True,
						primary_key=True,
						serialize=False,
						verbose_name='ID',
					),
				),
				('num', models.PositiveIntegerField()),
				('body', models.TextField()),
				(
					'created_at',
					models.DateTimeField(default=django.utils.timezone.now),
				),
				('edited_at', models.DateTimeField(blank=True, null=True)),
				('is_removed', models.BooleanField(db_index=True, default=False)),
				(
					'thread',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						related_name='posts',
						to='otodb.thread',
					),
				),
				(
					'user',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						to=settings.AUTH_USER_MODEL,
					),
				),
				(
					'edited_by',
					models.ForeignKey(
						blank=True,
						null=True,
						on_delete=django.db.models.deletion.SET_NULL,
						related_name='edited_threadposts',
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={'ordering': ['num']},
		),
		migrations.AddConstraint(
			model_name='threadpost',
			constraint=models.UniqueConstraint(
				fields=('thread', 'num'), name='threadpost_unique_num'
			),
		),
		migrations.AddConstraint(
			model_name='threadpost',
			constraint=models.CheckConstraint(
				condition=models.Q(('num__gt', 1)) | models.Q(('is_removed', False)),
				name='threadpost_op_kept',
			),
		),
		# Notifications now point at a specific post.
		migrations.AddField(
			model_name='notification',
			name='threadpost',
			field=models.ForeignKey(
				blank=True,
				null=True,
				on_delete=django.db.models.deletion.CASCADE,
				to='otodb.threadpost',
			),
		),
	]
