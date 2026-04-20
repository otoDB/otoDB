from django.db import models

from django.conf import settings
from .enums import Preferences


class UserPreference(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='preferences',
		null=False,
	)
	setting = models.IntegerField(choices=Preferences.choices, null=False)
	value = models.IntegerField(null=False)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['user', 'setting'],
				name='userpreference_single_value_for_setting',
			),
		]
