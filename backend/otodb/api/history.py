from typing import Literal
from datetime import datetime
from itertools import groupby

import diff_match_patch as dmp_mod

from django.contrib.contenttypes.models import ContentType

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


def rollback_entity(entity_id, entity_type, date, del_new_ids={}):
	if isinstance(entity_type, int):
		entity_type_id = entity_type
	elif isinstance(entity_type, str):
		entity_type_id = ContentType.objects.get(model=entity_type).id

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
	# if another entity that has been deleted - some model - this entity
	for ent_id, ent_type_id in (
		RevisionChangeEntity.objects.filter(
			change__in=del_rcs,
			change__target_id=F('entity_id'),
			change__target_type=F('entity_type'),
		)
		.exclude(entity_id=entity_id, entity_type_id=entity_type_id)
		.values_list('entity_id', 'entity_type_id')
		.distinct()
	):
		if (ent_type_id, ent_id) not in del_new_ids:
			rollback_entity(ent_id, ent_type_id, date, del_new_ids)

	for target_type_id, target_id in del_rcs.values_list(
		'target_id', 'target_type_id'
	).distinct():
		T = ContentType.objects.get(id=target_type_id).model_class()
		values = {
			field: RevisionChange.objects.filter(
				target_column=field,
				target_type_id=target_type_id,
				target_id=target_id,
				rev__date_lt=date,
			)
			.order_by('-rev__date')
			.first()
			.target_value
			for field in T.revision_tracked_fields
		}
		del_new_ids[(target_type_id, target_id)] = T.objects.create(**values).id

	for (target_type_id, target_id), target_columns in groupby(
		changes.filter(deleted=False)
		.values_list('target_type_id', 'target_id', 'target_column')
		.order_by('target_type_id', 'target_id')
		.all(),
		lambda v: (v[0], v[1]),
	):
		T = ContentType.objects.get(id=target_type_id).model_class()
		values = {}
		for field in target_columns:
			target_value = (
				RevisionChange.objects.filter(
					target_column=field,
					target_type_id=target_type_id,
					target_id=target_id,
					rev__date_lt=date,
				)
				.order_by('-rev__date')
				.first()
				.target_value
			)

			if isinstance(F, RelatedField):
				FF = T._meta.get_field(field)
				values[field] = getattr(
					del_new_ids,
					(
						ContentType.objects.get_for_model(FF.related_model).id,
						int(target_value),
					),
					target_value,
				)
			else:
				values[field] = target_value
		ContentType.objects.get(id=target_type_id).model_class().filter(
			id=getattr(del_new_ids, (target_type_id, target_id), target_id)
		).update(**values)


@history_router.post('rollback_ent', auth=django_auth)
@user_is_staff  # for now
@track_revision
def entity_rollback(request: HttpRequest, date: datetime, entity: EntitySchema):
	rollback_entity(entity.id, entity.entity, date)


@history_router.post('rollback', auth=django_auth)
@user_is_staff  # for now
def rollback(request: HttpRequest, revision_id: int):
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
def user_rollback(request: HttpRequest, date: datetime, username: str):
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
def history(request: HttpRequest, entity: EntitySchema = Query(...)):
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
