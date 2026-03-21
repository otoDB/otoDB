from django.db import models

from django.conf import settings
from .enums import ThemePref, LanguageTypes


class UserPreferences(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='prefs',
		null=False,
	)

	language = models.IntegerField(
		choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False
	)
	theme = models.IntegerField(
		choices=ThemePref.choices, default=ThemePref.DEFAULT, null=False
	)
