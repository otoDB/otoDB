from django.db import models

from otodb.account.models import Account
from .enums import ThemePref, LanguageTypes


class UserPreferences(models.Model):
	user = models.OneToOneField(
		Account, on_delete=models.CASCADE, related_name='prefs', null=False
	)

	language = models.IntegerField(
		choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False
	)
	theme = models.IntegerField(
		choices=ThemePref.choices, default=ThemePref.DEFAULT, null=False
	)
