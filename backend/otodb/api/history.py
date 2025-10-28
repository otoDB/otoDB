from typing import Literal
from datetime import datetime

import diff_match_patch as dmp_mod

from django.db.models import Window, F
from django.db.models.functions import RowNumber

from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router, ModelSchema, Field
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import TagWork, Revision, RevisionChange
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

	class Meta:
		model = Revision
		fields = ['message']


class RevisionChangeSchema(ModelSchema):
	target_type: str = Field(..., alias='target_type.model')

	class Meta:
		model = RevisionChange
		fields = ['target_id', 'deleted', 'target_column', 'target_value']


class FullRevisionSchema(RevisionSchema):
	changes: list[RevisionChangeSchema] = Field(..., alias='revisionchange_set')


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
	return Revision.objects.order_by('-id')


@history_router.get('user', response=list[RevisionSchema])
@paginate
def user(request: HttpRequest, username: str):
	return Revision.objects.filter(user=get_object_or_404(Account, username=username))


@history_router.get('revision', response=FullRevisionSchema)
def revision(request: HttpRequest, revision_id: int):
	return get_object_or_404(Revision, id=revision_id)


@history_router.post('rollback', auth=django_auth)
@user_is_staff  # for now
@track_revision
def rollback(request: HttpRequest, history_id: int):
	pass  # TODO


@history_router.get('history', auth=django_auth, response=list[RevisionSchema])
@paginate
def history(
	request: HttpRequest, object_id: int | str, entity: Literal['mediawork', 'tagwork']
):
	if entity == 'tagwork':
		object_id = TagWork.objects.get(slug=object_id).id
	return (
		Revision.objects.filter(
			revisionchange__revisionchangeentity__entity_id=object_id,
			revisionchange__revisionchangeentity__entity_type__model=entity,
		)
		.distinct()
		.annotate(index=Window(expression=RowNumber(), order_by=F('id').asc()))
		.order_by('-id')
	)
