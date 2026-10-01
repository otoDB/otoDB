from django.db import migrations, models

COUNT = models.IntegerField(
	default=0,
	editable=False,
	help_text='Number of rows in the instance table for this tag, maintained by DB triggers (otodb/db_triggers.py).',
)


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0123_worksource_unique_platform_source_id'),
	]

	operations = [
		migrations.RemoveField(model_name='tagwork', name='protected'),
		migrations.RemoveField(model_name='tagsong', name='protected'),
		migrations.AlterField(model_name='tagwork', name='count', field=COUNT),
		migrations.AlterField(model_name='tagsong', name='count', field=COUNT),
	]
