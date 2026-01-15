from typing import Literal, Any
from datetime import datetime
from itertools import groupby
import logging

import diff_match_patch as dmp_mod

from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection

from django.db.models import Window, F, Subquery, OuterRef, Exists
from django.db.models.functions import RowNumber
from django.db.models.fields.related import RelatedField

from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from django_cte import CTE, with_cte
from django_request_cache import get_request_cache

from ninja import Router, ModelSchema, Schema, Field, Query
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import (
	TagWork,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
	MediaWork,
)
from otodb.models.enums import RevisionChain
from otodb.account.models import Account

from .common import user_is_staff, track_revision

history_router = Router()

dmp = dmp_mod.diff_match_patch()
logger = logging.getLogger(__name__)


def get_diff(delta):
	def diff_prettyHtml(diffs):
		html = []
		for op, data in diffs:
			text = (
				data.replace('&', '&amp;')
				.replace('<', '&lt;')
				.replace('>', '&gt;')
				.replace('\n', '&para;<br>')
			)
			if op == dmp.DIFF_INSERT:
				html.append('<ins>%s</ins>' % text)
			elif op == dmp.DIFF_DELETE:
				html.append('<del>%s</del>' % text)
			elif op == dmp.DIFF_EQUAL:
				html.append('<span>%s</span>' % text)
		return ''.join(html)

	diffs_html = []

	for change in delta.changes:
		if change.field == 'tags':
			field = [f for f in (change.old + change.new)[0].keys() if 'tag' in f][0]
			old, new = {c[field] for c in change.old}, {c[field] for c in change.new}
			old, new = old - new, new - old
			changes = [
				'- ' + t
				for t in TagWork.objects.filter(id__in=old).values_list(
					'slug', flat=True
				)
			] + [
				'+ ' + t
				for t in TagWork.objects.filter(id__in=new).values_list(
					'slug', flat=True
				)
			]
			diffs_html.append({'html': ('<br>').join(changes), 'field': change.field})
		else:
			old, new = change.old, change.new
			diff_field = dmp.diff_main(str(old), str(new))
			dmp.diff_cleanupSemantic(diff_field)

			diffs_html.append(
				{
					'html': diff_prettyHtml(diff_field).replace('&para;', ''),
					'field': change.field,
				}
			)

	return diffs_html


class RevisionSchema(ModelSchema):
	id: int
	date: datetime
	user: str = Field(..., alias='user.username')
	index: None | int = None
	route: None | int = None

	class Meta:
		model = Revision
		fields = ['message']


class RevisionChangeSchema(ModelSchema):
	target_type: str = Field(..., alias='target_type.model')

	class Meta:
		model = RevisionChange
		fields = ['target_id', 'deleted', 'target_column', 'target_value']


class RevisionChangeEntitySchema(Schema):
	entity_type: str = Field(..., alias='entity_type__model')
	entity_id: int
	route: int


class FullRevisionSchema(RevisionSchema):
	# actions: list[RevisionChangeEntitySchema]
	pass


def get_history_dict(historical):
	d = model_to_dict(
		historical,
		fields=[
			'history_id',
			'history_date',
			'history_user',
			'history_change_reason',
		],
	) | {'delta': [], 'model': historical.model}
	if d['history_user']:
		d['history_user'] = Account.objects.get(id=d['history_user']).username
	else:
		d['history_user'] = Account.objects.get(id=1).username
	return d


@history_router.get('recent', response=list[RevisionSchema])
@paginate
def recent(request: HttpRequest, username: str | None = None):
	q = Revision.objects.annotate(
		route=Subquery(
			RevisionChangeEntity.objects.filter(change__rev_id=OuterRef('id')).values(
				'route'
			)[:1]
		)
	).order_by('-id')
	if username:
		q = q.filter(user__username=username)
	return q


@history_router.get('user', response=list[RevisionSchema])
@paginate
def user(request: HttpRequest, username: str):
	return Revision.objects.filter(user=get_object_or_404(Account, username=username))


@history_router.get('revision', response=FullRevisionSchema)
def revision(request: HttpRequest, revision_id: int):
	return get_object_or_404(Revision, id=revision_id)


@history_router.get('revision_changes', response=list[RevisionChangeSchema])
@paginate
def revision_changes(request: HttpRequest, revision_id: int):
	return get_object_or_404(Revision, id=revision_id).revisionchange_set.all()


class EntitySchema(Schema):
	id: int | str
	entity: Literal['mediawork', 'tagwork']


def find_rev_rst(ctpk, query_pk, rev):
	if q := RevisionChange.objects.filter(
		target_type_id=ctpk, target_id=query_pk, restored=True
	):
		return int(q.first().target_value)
	if (ctpk, query_pk) in rev:
		return rev[ctpk, query_pk]


def get_rev_restored(ctpk, pk):
	cache = get_request_cache()
	rev = cache.get('rev_rst')
	rev_del = cache.get('rev_del')

	while pk is not None:
		last = pk
		pk = find_rev_rst(ctpk, pk, rev)

	# Check if deleted
	if RevisionChange.objects.filter(
		target_type_id=ctpk, target_id=last, deleted=True
	).exists() or any([ctpk == ctid and last == idd for ctid, idd, _ in rev_del]):
		return None
	else:
		return last


def add_rev_restore(ctpk, pk, new_pk):
	assert pk != new_pk
	cache = get_request_cache()
	rev = cache.get('rev_rst')

	while pk is not None:
		last = pk
		pk = find_rev_rst(ctpk, pk, rev)

	assert RevisionChange.objects.filter(
		target_type_id=ctpk, target_id=last, deleted=True
	).exists()
	rev[(ctpk, last)] = new_pk
	cache.set('rev_rst', rev)


def _get_all_previous_field_values(
	model_class,
	target_type_id: int,
	target_id: int,
	date: datetime,
	related_targets: dict[tuple[int, int], list[tuple[str, int, int]]],
	fields: list[str] | None = None,
) -> tuple[bool, dict[str, Any]]:
	"""
	Fetch and convert previous values for all fields of an entity before a given date.

	Args:
		model_class: The Django model class
		target_type_id: ContentType ID of the target model
		target_id: ID of the target instance
		date: Rollback to state before this date
		fields: Optional list of specific fields to fetch (fetches all if None)

	Returns:
		(True, dictionary mapping field attnames to their converted values)
		(False, missing_fields)
	"""
	query = RevisionChange.objects.filter(
		target_type_id=target_type_id,
		target_id=target_id,
		rev__date__lt=date,
	)
	if fields:
		query = query.filter(target_column__in=fields)
	if connection.vendor == 'postgresql':
		qs = query.order_by('target_column', '-rev__date').distinct('target_column')
	else:
		annotated_qs = query.annotate(
			row_number=Window(
				expression=RowNumber(),
				partition_by=[F('target_column')],
				order_by=F('rev__date').desc(),
			)
		)
		qs = annotated_qs.filter(row_number=1)
	latest_changes = dict(qs.values_list('target_column', 'target_value'))

	# Check if we found all required fields
	required_fields = fields or model_class._revision_meta.tracked_fields
	missing_fields = set(required_fields) - set(latest_changes.keys())
	if missing_fields:
		return False, missing_fields

	# Pre-fetch field objects
	related_fields = {
		field_name: model_class._meta.get_field(field_name)
		for field_name in latest_changes.keys()
	}
	model_to_ct_id = {
		field_obj.related_model: ContentType.objects.get_for_model(
			field_obj.related_model
		).id
		for field_obj in related_fields.values()
		if isinstance(field_obj, RelatedField)
	}

	result = {}
	for field_name, target_value in latest_changes.items():
		field_obj = related_fields[field_name]

		if isinstance(field_obj, RelatedField):
			if target_value is not None:
				related_ct_id = model_to_ct_id[field_obj.related_model]
				if (target_type_id, target_id) not in related_targets:
					related_targets[(target_type_id, target_id)] = [
						(field_obj.attname, related_ct_id, int(target_value))
					]
				else:
					related_targets[(target_type_id, target_id)].append(
						(
							field_obj.attname,
							related_ct_id,
							int(target_value),
						)
					)
				result[field_obj.attname] = int(target_value)  # Ostrich
			else:
				result[field_obj.attname] = None
		else:
			result[field_obj.attname] = field_obj.to_python(target_value)

	return True, result


@transaction.atomic
def rollback_entity(
	entity_id: int | str,
	entity_type: int | str,
	date: datetime,
):
	"""
	Rollback an entity to its state before a given date.

	This function restores both deleted entities and updates to existing entities
	by examining the revision history. Related entities are handled recursively.

	Args:
		entity_id: The ID of the entity to rollback
		entity_type: Either a ContentType ID (int) or model name (str)
		date: Rollback all changes that occurred on or after this date
	"""
	first_rev = Revision.objects.order_by('date').first()
	if first_rev and date <= first_rev.date:
		raise ValueError('Not allowed to rollback to before the first revision')

	def rollback_entity_rec(
		entity_id: int | str,
		entity_type: int | str,
		related_targets: dict[tuple[int, int], list[tuple[str, int, int]]],
	) -> None:
		# Normalize entity_type to ContentType ID
		if isinstance(entity_type, int):
			entity_type_id = entity_type
		elif isinstance(entity_type, str):
			entity_type_id = ContentType.objects.get(model=entity_type).id
		else:
			logger.error(f'Invalid entity_type: {entity_type}')
			return

		logger.info(f'Rolling back entity {entity_type}:{entity_id} to {date}')

		# Get all changes associated with this entity since the rollback date
		changes = RevisionChange.objects.filter(
			id__in=RevisionChangeEntity.objects.filter(
				entity_id=entity_id,
				entity_type_id=entity_type_id,
				change__rev__date__gte=date,
			).values_list('change_id', flat=True)
		)

		# Changes tagged with this entity may not tell us it's deleted if the FK/1-1 was changed to another entity before deletion
		# So we need to re-query with a correlated Table.Row
		del_rcs = (
			RevisionChange.objects.filter(rev__date__gte=date)
			.filter(
				Exists(
					changes.filter(
						target_type_id=OuterRef('target_type_id'),
						target_id=OuterRef('target_id'),
					)
				)
			)
			.filter(deleted=True)
		)

		# Recursively rollback related entities that were deleted.
		# If a related entity (FK/OneToOne pointing to this entity) was deleted,
		# we need to restore it first before we can restore this entity's references to it.
		related_entities = (
			RevisionChangeEntity.objects.filter(
				change__in=del_rcs,
				change__target_id=F('entity_id'),
				change__target_type=F('entity_type'),
			)
			.exclude(entity_id=entity_id, entity_type_id=entity_type_id)
			.values_list('entity_id', 'entity_type_id')
			.distinct()
		)
		for ent_id, ent_type_id in related_entities:
			if (
				get_rev_restored(ent_type_id, ent_id) == ent_id
				and ContentType.objects.get(id=ent_type_id)
				.model_class()
				._revision_meta.chain
				== RevisionChain.STRONG
			):
				rollback_entity_rec(ent_id, ent_type_id, related_targets)

		# Bulk fetch all unique ContentTypes we'll need
		deleted_targets = del_rcs.values_list('target_type_id', 'target_id').distinct()
		content_type_ids = set(ct_id for ct_id, _ in deleted_targets)

		# Also get content types for modified entities
		modified_targets = (
			changes.filter(deleted=False)
			.values_list('target_type_id', 'target_id')
			.distinct()
		)
		content_type_ids.update(ct_id for ct_id, _ in modified_targets)
		content_types = ContentType.objects.in_bulk(list(content_type_ids))

		# Restore deleted entities
		for target_type_id, target_id in deleted_targets:
			model_class = content_types[target_type_id].model_class()
			if model_class is None:
				logger.error(
					f'Could not get model class for ContentType ID {target_type_id}'
				)
				return

			try:
				completed, values = _get_all_previous_field_values(
					model_class, target_type_id, target_id, date, related_targets
				)
			except ValueError as e:
				logger.error(f'{e}, cannot restore deleted entity')
				raise

			if completed:
				try:
					for field_name in set(
						model_class._revision_meta.tracked_fields
					) - set(model_class._revision_meta.entity_attrs):
						FF = model_class._meta.get_field(field_name)
						if isinstance(FF, RelatedField):
							R = FF.related_model
							if not FF.null and hasattr(R, '_revision_meta'):
								assert (field_name + '_id') in values
								rel = (
									RevisionChange.objects.filter(
										target_type=ContentType.objects.get_for_model(
											R
										),
										target_id=values[field_name + '_id'],
										rev__date__lt=date,
									)
									.order_by('-rev__date')
									.first()
								)
								for ent in rel.revisionchangeentity_set.all():
									if (
										ent.entity_type_id != entity_type_id
										and not get_rev_restored(
											ent.entity_type_id, ent.entity_id
										)
									):
										rollback_entity_rec(
											ent.entity_id,
											ent.entity_type_id,
											related_targets,
										)

					# ...I'm not exactly sure why this check makes a difference, but it does
					if new_id := get_rev_restored(target_type_id, target_id):
						npk = new_id
						created = False
						model_class.objects.filter(id=new_id).update(**values)
					else:
						new_instance, created = model_class.objects.update_or_create(
							**values
						)
						npk = new_instance.pk
					if created:
						add_rev_restore(target_type_id, target_id, npk)
						logger.debug(
							f'Restored deleted {model_class.__name__} (old_id={target_id}, new_id={npk})'
						)
					else:
						logger.debug(
							f'Restored {model_class.__name__} (old_id={target_id}, new_id={npk}) by updating'
						)
				except Exception as e:
					logger.error(
						f'Failed to restore {model_class.__name__} (id={target_id}): {e}'
					)
					raise

		# Update modified entities using bulk operations
		# Group by (target_type_id, target_id) to batch updates per entity
		updates_by_model = {}  # model_class -> list of (instance_id, field_updates)
		delete_models = {}

		for (target_type_id, target_id), target_columns in groupby(
			changes.filter(deleted=False)
			.values_list('target_type_id', 'target_id', 'target_column')
			.order_by('target_type_id', 'target_id'),
			lambda v: (v[0], v[1]),
		):
			model_class = content_types[target_type_id].model_class()
			if model_class is None:
				logger.error(
					f'Could not get model class for ContentType ID {target_type_id}'
				)
				return

			actual_target_id = get_rev_restored(target_type_id, target_id)
			if actual_target_id:
				# Extract just the field names
				fields_to_fetch = [
					field_name_tuple[2] for field_name_tuple in target_columns
				]
				try:
					completed, values = _get_all_previous_field_values(
						model_class,
						target_type_id,
						target_id,
						date,
						related_targets,
						fields=fields_to_fetch,
					)
				except ValueError as e:
					logger.error(f'{e}, skipping entity')
					raise
				except Exception as e:
					logger.warning(f'Could not process {model_class.__name__}: {e}')
				if completed:
					if model_class not in updates_by_model:
						updates_by_model[model_class] = []
					updates_by_model[model_class].append((actual_target_id, values))
				elif set(fields_to_fetch) == values:
					if model_class not in delete_models:
						delete_models[model_class] = []
					delete_models[model_class].append(actual_target_id)

		# Execute bulk updates per model
		for model_class, updates in updates_by_model.items():
			for instance_id, field_updates in updates:
				try:
					model_class.objects.filter(id=instance_id).update(**field_updates)
					logger.debug(
						f'Updated {model_class.__name__} (id={instance_id}) with {len(field_updates)} fields'
					)
				except Exception as e:
					logger.error(
						f'Failed to update {model_class.__name__} (id={instance_id}): {e}'
					)
					raise

		for model_class, target_ids in delete_models.items():
			model_class.objects.filter(id__in=target_ids).delete()

	related_targets = {}
	with connection.constraint_checks_disabled():
		rollback_entity_rec(entity_id, entity_type, related_targets)
		for (ctid, rid), fs in related_targets.items():
			# Apply to_active to resolve soft deletes (aliased_to/moved_to)
			changes = {}
			for f, rctid, v in fs:
				vv = get_rev_restored(rctid, v)
				model_class = ContentType.objects.get(id=rctid).model_class()
				if (
					model_class
					and hasattr(model_class, '_revision_meta')
					and model_class._revision_meta.to_active
				):
					vv = model_class._revision_meta.to_active(
						model_class.objects.get(pk=v)
					).pk
				changes[f] = vv
			ContentType.objects.get(id=ctid).model_class().objects.filter(
				id=get_rev_restored(ctid, rid)
			).update(**changes)


@history_router.post('rollback', auth=django_auth)
@user_is_staff  # for now
@track_revision
@transaction.atomic
def rollback(
	request: HttpRequest, revision_id: int, entity: EntitySchema | None = None
):
	"""
	Rollback changes of a specific revision.

	If entity is not provided: rollback all changes made IN the specified revision.
	If entity is provided: rollback that entity TO its state at the specified revision.
	"""
	rev = get_object_or_404(Revision, id=revision_id)

	if entity is None:
		# Rollback all entities affected by this revision
		for ent in (
			RevisionChangeEntity.objects.filter(change__rev=rev)
			.values('entity_id', 'entity_type__model')
			.distinct()
			.all()
		):
			rollback_entity(ent['entity_id'], ent['entity_type__model'], rev.date)
	else:
		# Rollback specific entity TO the state at this revision
		# Get the next revision after the specified one
		next_rev = Revision.objects.filter(id__gt=revision_id).order_by('id').first()
		if next_rev is not None:
			# Rollback to the state before the next revision
			rollback_entity(entity.id, entity.entity, next_rev.date)
		# If no next revision, entity is already in that state (no-op)


@history_router.post('rollback_user', auth=django_auth)
@user_is_staff
@track_revision
@transaction.atomic
def user_rollback(request: HttpRequest, date: datetime, username: str):
	"""Rollback all changes made by a specific user since the given date."""
	for ent in (
		RevisionChangeEntity.objects.filter(
			change__rev__date__gte=date,
			change__rev__user=get_object_or_404(Account, username=username),
		)
		.values('entity_id', 'entity_type__model')
		.distinct()
		.all()
	):
		rollback_entity(ent['entity_id'], ent['entity_type__model'], date)


@history_router.get('history', response=list[RevisionSchema])
@paginate
def history(request: HttpRequest, entity: Query[EntitySchema]):
	query_ids = []
	match entity.entity:
		case 'mediawork':
			work = MediaWork.objects.get(id=entity.id)
			while work.moved_to:
				work = work.moved_to
			entity.id = work.pk
			cte = CTE.recursive(
				lambda cte: MediaWork.objects.order_by()
				.filter(pk=work.pk)
				.values('id')
				.union(
					cte.join(
						MediaWork.objects.order_by(),
						moved_to_id=cte.col.id,
					).values('id'),
					all=True,
				)
			)
			merged = (
				with_cte(cte, select=cte.join(TagWork, id=cte.col.id))
				.exclude(pk=work.pk)
				.distinct()
				.order_by()
			)
			query_ids = query_ids + [*merged.values_list('id', flat=True)]

		case 'tagwork':
			tag = TagWork.objects.get(slug=entity.id)
			if tag.aliased_to:
				tag = tag.aliased_to
			entity.id = tag.pk
			query_ids = query_ids + [*tag.aliases.values_list('id', flat=True)]
	query_ids.append(entity.id)
	return (
		Revision.objects.filter(
			id__in=Subquery(
				Revision.objects.filter(
					revisionchange__revisionchangeentity__entity_id__in=query_ids,
					revisionchange__revisionchangeentity__entity_type__model=entity.entity,
				)
				.distinct()
				.values('id')
			)
		)
		.annotate(
			index=Window(expression=RowNumber(), order_by=F('id').asc()),
			route=Subquery(
				RevisionChangeEntity.objects.filter(
					change__rev_id=OuterRef('id')
				).values('route')[:1]
			),
		)
		.order_by('-index')
	)
