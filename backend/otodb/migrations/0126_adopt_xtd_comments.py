from django.db import migrations

# Tables left behind by django-comments-xtd, django-contrib-comments and
# django.contrib.sites
OLD_TABLES = [
	'django_comment_flags',
	'django_comments_xtd_blacklisteddomain',
	'django_comments_xtd_xtdcomment',
	'django_comments',
	'django_site',
]
OLD_APPS = ['django_comments_xtd', 'django_comments', 'sites']


def forward(apps, schema_editor):
	"""Move comments out of django-comments-xtd's tables into otodb_comment.

	0001 now creates otodb_comment directly, so this only does something on
	databases that were migrated while django-comments-xtd was installed."""
	connection = schema_editor.connection
	if 'django_comments_xtd_xtdcomment' not in connection.introspection.table_names():
		return

	Comment = apps.get_model('otodb', 'Comment')
	Notification = apps.get_model('otodb', 'Notification')
	CommentMeta = apps.get_model('otodb', 'CommentMeta')

	schema_editor.create_model(Comment)
	# Keep the ids so notifications and edit metadata still point at the same
	# comments. Top-level comments were their own parent; they are now 0.
	schema_editor.execute(
		"""
		INSERT INTO otodb_comment
			(id, content_type_id, object_pk, user_id, comment, submit_date,
			is_removed, parent_id, level)
		SELECT
			c.id, c.content_type_id, c.object_pk::bigint, c.user_id, c.comment,
			c.submit_date, c.is_removed,
			CASE WHEN x.parent_id = c.id THEN 0 ELSE x.parent_id END, x.level
		FROM django_comments c
		JOIN django_comments_xtd_xtdcomment x ON x.comment_ptr_id = c.id
		"""
	)
	schema_editor.execute(
		"SELECT setval(pg_get_serial_sequence('otodb_comment', 'id'), "
		'COALESCE(MAX(id), 0) + 1, false) FROM otodb_comment'
	)

	# CASCADE also drops the foreign keys from otodb_notification and
	# otodb_commentmeta, which are re-added below against otodb_comment.
	for table in OLD_TABLES:
		schema_editor.execute(
			f'DROP TABLE IF EXISTS {schema_editor.quote_name(table)} CASCADE'
		)
	for model in (Notification, CommentMeta):
		field = model._meta.get_field('comment')
		schema_editor.execute(
			schema_editor._create_fk_sql(model, field, '_fk_%(to_table)s_%(to_column)s')
		)

	# Their content types are left for `manage.py remove_stale_contenttypes`.
	schema_editor.execute(
		'DELETE FROM django_migrations WHERE app = ANY(%s)', [OLD_APPS]
	)


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0125_tag_trigram_indexes'),
	]

	operations = [
		migrations.RunPython(forward),
	]
