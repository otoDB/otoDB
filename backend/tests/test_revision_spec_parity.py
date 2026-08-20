"""While Django exists, assert otodb/revision_spec.py still matches the models'
RevisionMeta + field types, so the Django-free trigger spec can't silently drift.

This test is deleted together with Django; after that revision_spec.py is the sole
source of truth for the capture triggers.
"""

from django.apps import apps

from otodb.models.revision import RevisionTrackedModel
from otodb.revision_spec import TABLES

_INT = {
	'IntegerField',
	'PositiveIntegerField',
	'PositiveSmallIntegerField',
	'SmallIntegerField',
	'BigIntegerField',
	'PositiveBigIntegerField',
	'AutoField',
	'BigAutoField',
}
_STR = {'CharField', 'TextField', 'SlugField'}
_KINDS = {'BooleanField': 'bool', 'FloatField': 'float', 'DateField': 'date'}


def _kind(field):
	"""Map a Django field to its trigger serialization kind.

	An unmapped type (DateTimeField, JSONField, ...) raises,
	so that tracking a field of a new type fails THIS test until a byte-parity
	serialization for it is designed in revision_codegen.
	"""
	if field.is_relation:
		return 'fk'
	internal = field.get_internal_type()
	if internal in _KINDS:
		return _KINDS[internal]
	if internal in _INT:
		return 'int'
	if internal in _STR:
		return 'str'
	raise AssertionError(
		f'{field.model.__name__}.{field.name}: no serialization kind for {internal};'
		' design one in revision_codegen._serialize and map it'
	)


def _expected_from_models():
	specs = {}
	for model in apps.get_models():
		if not issubclass(model, RevisionTrackedModel) or model._meta.abstract:
			continue
		meta = getattr(model, '_revision_meta', None)
		if not (meta and meta.tracked_fields):
			continue
		opts = model._meta
		tracked = []
		entities = []
		for name in meta.tracked_fields:
			f = opts.get_field(name)
			tracked.append((f.name, f.column, _kind(f)))
		for attr in meta.entity_attrs:
			if attr == 'self':
				entities.append(
					('self', opts.app_label, opts.model_name, opts.pk.column)
				)
			else:
				f = opts.get_field(attr)
				rel = f.related_model._meta
				entities.append(('fk', rel.app_label, rel.model_name, f.column))
		specs[opts.db_table] = {
			'table': opts.db_table,
			'app': opts.app_label,
			'model': opts.model_name,
			'pk': opts.pk.column,
			'tracked': tracked,
			'entities': entities,
		}
	return specs


def test_spec_matches_models():
	expected = _expected_from_models()
	spec = {t['table']: t for t in TABLES}

	assert set(spec) == set(expected), 'revision_spec tables differ from tracked models'
	for table, want in expected.items():
		got = spec[table]
		# normalise the tuple/list distinction that survives round-tripping
		assert [tuple(t) for t in got['tracked']] == [
			tuple(t) for t in want['tracked']
		], f'{table}: tracked fields drifted'
		assert [tuple(e) for e in got['entities']] == [
			tuple(e) for e in want['entities']
		], f'{table}: entity routing drifted'
		assert (got['app'], got['model'], got['pk']) == (
			want['app'],
			want['model'],
			want['pk'],
		)
