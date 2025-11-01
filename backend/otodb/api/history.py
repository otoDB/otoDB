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
	changes: list[RevisionChangeSchema] = Field(..., alias='revisionchange_set')
	actions: list[RevisionChangeEntitySchema]


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
def recent(request: HttpRequest):
	return Revision.objects.annotate(
		route=Subquery(
			RevisionChangeEntity.objects.filter(change__rev_id=OuterRef('id')).values(
				'route'
			)[:1]
		)
	).order_by('-id')


@history_router.get('user', response=list[RevisionSchema])
@paginate
def user(request: HttpRequest, username: str):
	return Revision.objects.filter(user=get_object_or_404(Account, username=username))


@history_router.get('revision', response=FullRevisionSchema)
def revision(request: HttpRequest, revision_id: int):
	return get_object_or_404(Revision, id=revision_id)


class EntitySchema(Schema):
	id: int | str
	entity: Literal['mediawork', 'tagwork']


def _get_all_previous_field_values(
	model_class,
	target_type_id: int,
	target_id: int,
	date: datetime,
	del_new_ids: dict[tuple[int, int], int],
	fields: list[str] | None = None,
) -> dict[str, Any]:
	"""
	Fetch and convert previous values for all fields of an entity before a given date.

	Args:
		model_class: The Django model class
		target_type_id: ContentType ID of the target model
		target_id: ID of the target instance
		date: Rollback to state before this date
		del_new_ids: Mapping of (content_type_id, old_id) -> new_id for recreated entities
		fields: Optional list of specific fields to fetch (fetches all if None)

	Returns:
		Dictionary mapping field attnames to their converted values

	Raises:
		ValueError: If no previous revision is found for any required field
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
	required_fields = fields or getattr(model_class, 'revision_tracked_fields', [])
	missing_fields = set(required_fields) - set(latest_changes.keys())
	if missing_fields:
		raise ValueError(
			f'Incomplete history for {model_class.__name__} (id={target_id}). '
			f'Missing fields: {missing_fields}'
		)

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
				actual_id = del_new_ids.get(
					(related_ct_id, int(target_value)), int(target_value)
				)
				result[field_obj.attname] = actual_id
			else:
				result[field_obj.attname] = None
		else:
			result[field_obj.attname] = field_obj.to_python(target_value)

	return result


@transaction.atomic
def rollback_entity(
	entity_id: int | str,
	entity_type: int | str,
	date: datetime,
	del_new_ids: dict[tuple[int, int], int] | None = None,
) -> None:
	"""
	Rollback an entity to its state before a given date.

	This function restores both deleted entities and updates to existing entities
	by examining the revision history. Related entities are handled recursively.

	Args:
		entity_id: The ID of the entity to rollback
		entity_type: Either a ContentType ID (int) or model name (str)
		date: Rollback all changes that occurred on or after this date
		del_new_ids: Mapping of (content_type_id, old_id) -> new_id for recreated entities
	"""
	if del_new_ids is None:
		del_new_ids = {}

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
		if (ent_type_id, ent_id) not in del_new_ids:
			rollback_entity(ent_id, ent_type_id, date, del_new_ids)

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
			values = _get_all_previous_field_values(
				model_class, target_type_id, target_id, date, del_new_ids
			)
		except ValueError as e:
			logger.error(f'{e}, cannot restore deleted entity')
			return

		try:
			new_instance = model_class.objects.create(**values)
			del_new_ids[(target_type_id, target_id)] = new_instance.pk
			logger.debug(
				f'Restored deleted {model_class.__name__} (old_id={target_id}, new_id={new_instance.pk})'
			)
		except Exception as e:
			logger.error(
				f'Failed to restore {model_class.__name__} (id={target_id}): {e}'
			)

	# Update modified entities using bulk operations
	# Group by (target_type_id, target_id) to batch updates per entity
	updates_by_model = {}  # model_class -> list of (instance_id, field_updates)

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

		actual_target_id = del_new_ids.get((target_type_id, target_id), target_id)

		# Extract just the field names
		fields_to_fetch = [field_name_tuple[2] for field_name_tuple in target_columns]
		try:
			values = _get_all_previous_field_values(
				model_class,
				target_type_id,
				target_id,
				date,
				del_new_ids,
				fields=fields_to_fetch,
			)
		except ValueError as e:
			logger.error(f'{e}, skipping entity')
			return
		except Exception as e:
			logger.warning(f'Could not process {model_class.__name__}: {e}')
			continue

		if values:
			if model_class not in updates_by_model:
				updates_by_model[model_class] = []
			updates_by_model[model_class].append((actual_target_id, values))

	# Execute bulk updates per model
	for model_class, updates in updates_by_model.items():
		pks = [pk for pk, _ in updates]
		updates_by_pk = {pk: data for pk, data in updates}

		objects_to_update = []
		all_fields = set()

		for obj in model_class.objects.filter(pk__in=pks):
			update_data = updates_by_pk.get(obj.pk)
			if update_data:
				for field, value in update_data.items():
					setattr(obj, field, value)
					all_fields.add(field)
				objects_to_update.append(obj)

		if objects_to_update:
			model_class.objects.bulk_update(
				objects_to_update, fields=list(all_fields), batch_size=500
			)
			logger.debug(
				f'Bulk updated {len(objects_to_update)} {model_class.__name__} instances '
				f'with fields: {", ".join(all_fields)}'
			)


@history_router.post('rollback_ent', auth=django_auth)
@user_is_staff  # for now
@track_revision
@transaction.atomic
def entity_rollback(request: HttpRequest, date: datetime, entity: EntitySchema):
	"""Rollback a specific entity to its state before the given date."""
	rollback_entity(entity.id, entity.entity, date)


@history_router.post('rollback', auth=django_auth)
@user_is_staff  # for now
@track_revision
@transaction.atomic
def rollback(request: HttpRequest, revision_id: int):
	"""Rollback all changes made in a specific revision."""
	rev = get_object_or_404(Revision, id=revision_id)
	for ent in (
		RevisionChangeEntity.objects.filter(change__rev=rev)
		.values('entity_id', 'entity_type__model')
		.distinct()
		.all()
	):
		rollback_entity(ent['entity_id'], ent['entity_type__model'], rev.date)


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


@history_router.get('history', auth=django_auth, response=list[RevisionSchema])
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
