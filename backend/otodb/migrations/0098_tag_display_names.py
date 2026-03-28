import logging
import re
import unicodedata

from django.db import migrations
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def _slugify_tag(s):
	"""Snapshot of slugify_tag at migration time."""
	canonical = unicodedata.normalize('NFKC', s).strip().lower().replace(' ', '_')
	return slugify(canonical, allow_unicode=True)


def convert_underscores_to_spaces(apps, schema_editor):
	"""Convert underscores to spaces in existing tag names, and fix slugs
	that have hyphens where underscores are expected.
	Skips name changes where the conversion would collide with an existing name.
	"""
	for model_name in ('TagWork', 'TagSong'):
		model = apps.get_model('otodb', model_name)
		for tag in model.objects.all().iterator():
			updates = {}

			# Fix slug: replace hyphens with underscores where they were
			# introduced by Django's slugify (not tagulous collision suffixes)
			expected_slug = _slugify_tag(tag.name)
			if expected_slug and tag.slug != expected_slug:
				# Check if slug is the expected slug with a collision suffix
				suffix_match = re.fullmatch(
					rf'{re.escape(expected_slug)}(_\d+)', tag.slug
				)
				if not suffix_match:
					# Slug has hyphens from old Django slugify — fix them
					fixed_slug = tag.slug.replace('-', '_')
					fixed_expected = _slugify_tag(tag.name)
					if re.fullmatch(rf'{re.escape(fixed_expected)}(_\d+)?', fixed_slug):
						if not model.objects.filter(slug=fixed_slug).exists():
							updates['slug'] = fixed_slug

			# Convert underscores to spaces in name
			new_name = tag.name.replace('_', ' ')
			if new_name != tag.name:
				if not model.objects.filter(name=new_name).exists():
					updates['name'] = new_name
				else:
					logger.warning(
						'%s %d: skipped rename "%s" -> "%s" (collision)',
						model_name,
						tag.pk,
						tag.name,
						new_name,
					)

			if updates:
				model.objects.filter(pk=tag.pk).update(**updates)


def convert_spaces_to_underscores(apps, schema_editor):
	"""Reverse: convert spaces back to underscores.
	Skips tags where the conversion would collide with an existing name.
	"""
	for model_name in ('TagWork', 'TagSong'):
		model = apps.get_model('otodb', model_name)
		for tag in model.objects.all().iterator():
			new_name = tag.name.replace(' ', '_')
			if new_name != tag.name:
				if not model.objects.filter(name=new_name).exists():
					model.objects.filter(pk=tag.pk).update(name=new_name)


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0097_alter_mediasongconnection_site'),
	]

	operations = [
		migrations.RunPython(
			convert_underscores_to_spaces,
			convert_spaces_to_underscores,
		),
	]
