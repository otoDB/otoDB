from django.apps import AppConfig
from django.db import connections
from django.db.models.signals import post_migrate


def _install_db_triggers(sender, using, **kwargs):
	"""Runs after every `migrate`."""
	from otodb.db_triggers import install_db_triggers

	install_db_triggers(connections[using])


class OtodbConfig(AppConfig):
	name = 'otodb'

	def ready(self):
		# connect @receivers
		from . import signals  # noqa: F401

		post_migrate.connect(_install_db_triggers, sender=self)
