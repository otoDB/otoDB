"""
Prints the OpenAPI Schema to stdout.
"""

import json

from django.core.management.base import BaseCommand

from otodb.api import api
from otodb_next.app import app as otodb_new


class Command(BaseCommand):
	help = 'Exports Django Ninja OpenAPI schema to JSON'

	def handle(self, *args, **options):
		schema = api.get_openapi_schema()
		schema_new = otodb_new.openapi_schema.to_schema()
		for path, methods in schema_new['paths'].items():
			if path in schema['paths']:
				schema['paths'][path] = schema['paths'][path] | methods
			else:
				schema['paths'][path] = methods
		schema['components']['schemas'] = (
			schema['components']['schemas'] | schema_new['components']['schemas']
		)

		print(json.dumps(schema, indent=2))
