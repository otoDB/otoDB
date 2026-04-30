from urllib.parse import unquote

from django.db import models
from django.utils.encoding import uri_to_iri


class IRICharField(models.CharField):
	"""
	CharField that fully decodes percent-escapes on save.
	For opaque path segments (e.g. connection content_ids) where
	reserved-character preservation is irrelevant.
	"""

	def get_prep_value(self, value):
		value = super().get_prep_value(value)
		return None if value is None else unquote(value)


class IRIURLField(models.URLField):
	"""
	URLField that converts URIs to IRIs on save.
	Preserves reserved-character escapes so query-strings aren't corrupted.
	"""

	def get_prep_value(self, value):
		value = super().get_prep_value(value)
		return None if value is None else uri_to_iri(value)
