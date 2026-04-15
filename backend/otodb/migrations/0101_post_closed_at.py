from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0100_alter_revisionchangeentity_route'),
	]

	operations = [
		migrations.AddField(
			model_name='post',
			name='closed_at',
			field=models.DateTimeField(blank=True, null=True),
		),
	]
