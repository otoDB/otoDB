from django.apps import AppConfig


class OtodbConfig(AppConfig):
	name = 'otodb'

	def ready(self):
		# connect @receivers
		from . import signals  # noqa: F401
