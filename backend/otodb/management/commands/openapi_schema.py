"""
Prints the OpenAPI Schema to stdout.
"""

from django.core.management.base import BaseCommand
import json
from otodb.api import api


class Command(BaseCommand):
	help = 'Exports Django Ninja OpenAPI schema to JSON'

	def handle(self, *args, **options):
		schema = api.get_openapi_schema()
		print(json.dumps(schema, indent=2))
