"""
Prints the AppConfig JSON to stdout.
"""

import orjson
from django.core.management.base import BaseCommand

from otodb.api import SHARED_CONFIG


class Command(BaseCommand):
	help = 'Exports otoDB API AppConfig to JSON'

	def handle(self, *args, **options):
		print(orjson.dumps(SHARED_CONFIG.dict()).decode('utf-8'), end='')
