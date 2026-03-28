import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def convert_underscores_to_spaces(apps, schema_editor):
	"""Convert underscores to spaces in existing tag names.
	Skips tags where the conversion would collide with an existing name.
	"""
	for model_name in ('TagWork', 'TagSong'):
		model = apps.get_model('otodb', model_name)
		for tag in model.objects.all().iterator():
			new_name = tag.name.replace('_', ' ')
			if new_name != tag.name:
				if not model.objects.filter(name=new_name).exists():
					model.objects.filter(pk=tag.pk).update(name=new_name)
				else:
					logger.warning(
						'%s %d: skipped rename "%s" -> "%s" (collision)',
						model_name,
						tag.pk,
						tag.name,
						new_name,
					)


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
