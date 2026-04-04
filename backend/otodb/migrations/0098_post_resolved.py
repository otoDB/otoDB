from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otodb', '0097_alter_mediasongconnection_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
