from django.apps import AppConfig
from django.db import connections
from django.db.models.signals import post_migrate


def install_revision_triggers(sender, using, **kwargs):
	"""Installs the revision triggers from the current spec. Runs after every `migrate`."""
	from otodb.revision_codegen import generate_sql
	from otodb.revision_spec import TABLES

	connection = connections[using]
	existing = set(connection.introspection.table_names())
	if any(spec['table'] not in existing for spec in TABLES):
		return
	with connection.cursor() as cursor:
		cursor.execute(generate_sql())


class OtodbConfig(AppConfig):
	name = 'otodb'

	def ready(self):
		# connect @receivers
		from . import signals  # noqa: F401

		post_migrate.connect(install_revision_triggers, sender=self)
