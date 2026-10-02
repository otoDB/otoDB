import django.contrib.postgres.indexes
import django.db.models.functions.text
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0124_remove_tag_protected'),
	]

	operations = [
		TrigramExtension(),
		migrations.AddIndex(
			model_name='tagsong',
			index=django.contrib.postgres.indexes.GinIndex(
				django.contrib.postgres.indexes.OpClass(
					models.F('slug'), name='gin_trgm_ops'
				),
				name='otodb_tagsong_slug_trgm',
				fastupdate=False,
			),
		),
		migrations.AddIndex(
			model_name='tagsong',
			index=django.contrib.postgres.indexes.GinIndex(
				django.contrib.postgres.indexes.OpClass(
					django.db.models.functions.text.Upper('name'), name='gin_trgm_ops'
				),
				name='otodb_tagsong_name_trgm',
				fastupdate=False,
			),
		),
		migrations.AddIndex(
			model_name='tagwork',
			index=django.contrib.postgres.indexes.GinIndex(
				django.contrib.postgres.indexes.OpClass(
					models.F('slug'), name='gin_trgm_ops'
				),
				name='otodb_tagwork_slug_trgm',
				fastupdate=False,
			),
		),
		migrations.AddIndex(
			model_name='tagwork',
			index=django.contrib.postgres.indexes.GinIndex(
				django.contrib.postgres.indexes.OpClass(
					django.db.models.functions.text.Upper('name'), name='gin_trgm_ops'
				),
				name='otodb_tagwork_name_trgm',
				fastupdate=False,
			),
		),
	]
