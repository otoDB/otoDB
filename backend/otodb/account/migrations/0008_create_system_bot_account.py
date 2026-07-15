from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_system_account(apps, schema_editor):
	Account = apps.get_model('account', 'Account')
	username = settings.OTODB_SYSTEM_BOT_USERNAME
	if Account.objects.filter(username=username).exists():
		return
	account = Account(
		username=username,
		email=f'{username.lower()}@otodb.invalid',
		level=40,  # Levels.EDITOR
		is_active=False,
		email_activated=True,
		password=make_password(None),  # Equivalent to unusable password
	)
	account.save()


def delete_system_account(apps, schema_editor):
	Account = apps.get_model('account', 'Account')
	Account.objects.filter(username=settings.OTODB_SYSTEM_BOT_USERNAME).delete()


class Migration(migrations.Migration):
	dependencies = [
		('account', '0007_alter_invitation_created_at_alter_invitation_used_by'),
	]

	operations = [
		migrations.RunPython(create_system_account, reverse_code=delete_system_account),
	]
