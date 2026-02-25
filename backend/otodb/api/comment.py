from datetime import datetime

from typing import Literal

from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType

from django.db.models import Window
from django.db.models.functions import Rank

from django_comments_xtd.models import XtdComment

from pydantic import field_validator

from ninja import Router, Schema
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.account.models import Account
from otodb.markdown import render_markdown
from otodb.models import Notification, Subscription
from .common import user_is_trusted, ProfileSchema, mentioned_user_ids

comment_router = Router()

ModelsWithComments = Literal[
	'mediawork',
	'account',
	'pool',
	'tagwork',
	'tagsong',
	'post',
	'bulkrequest',
]


class CommentSchema(Schema):
	id: int
	level: int
	user: ProfileSchema
	comment: str
	submit_date: datetime
	parent_id: int
	index: int

	@field_validator('comment', mode='before')
	@classmethod
	def render_comment(cls, v: str) -> str:
		return render_markdown(v)


@comment_router.get('comments', response=list[CommentSchema])
def get(request: HttpRequest, model: ModelsWithComments, pk: int):
	T = ContentType.objects.get(model=model)
	index = Window(
		expression=Rank(),
		order_by='submit_date',
	)
	# Use comprehension to force filter after annotate
	return [
		c
		for c in XtdComment.objects.filter(content_type=T, object_pk=pk)
		.order_by('id')
		.annotate(index=index)
		if not c.is_removed
	]


@comment_router.post('comment', auth=django_auth, throttle=[AuthRateThrottle('1/8s')])
@user_is_trusted
def post(
	request: HttpRequest,
	model: ModelsWithComments,
	pk: int,
	comment_text: str,
	parent_id: int = 0,
):
	T = ContentType.objects.get(model=model)
	parent = None if parent_id == 0 else XtdComment.objects.get(id=parent_id)
	if parent is not None and parent.is_removed:
		return 400

	comment = XtdComment.objects.create(
		content_type=T,
		object_pk=pk,
		site_id=1,
		user=request.user,
		comment=comment_text,
		parent_id=parent_id,
	)

	target_ids: set[int] = set()
	if parent is None:
		target_ids |= set(
			Subscription.objects.filter(entity_type=T, entity_id=pk)
			.exclude(subscriber_id=request.user.pk)
			.values_list('subscriber_id', flat=True)
		)
		Subscription.objects.get_or_create(
			subscriber=request.user, entity_type=T, entity_id=pk
		)
	else:
		target_ids.add(parent.user_id)
	if model == 'account' and pk != request.user.pk:
		target_ids.add(pk)

	target_ids |= mentioned_user_ids(comment_text, exclude_user_id=request.user.pk)
	target_ids.discard(request.user.pk)

	Notification.objects.bulk_create(
		[Notification(target_id=target_id, comment=comment) for target_id in target_ids]
	)


@comment_router.delete('comment', auth=django_auth)
@user_is_trusted
def delete(
	request: HttpRequest,
	model: ModelsWithComments,
	pk: int,
	comment_id: int,
):
	T = ContentType.objects.get(model=model)
	comment = XtdComment.objects.get(
		content_type=T, object_pk=pk, site_id=1, id=comment_id
	)
	if request.user.level >= Account.Levels.ADMIN or comment.user == request.user:
		comment.is_removed = True
		comment.save()
		Notification.objects.filter(comment=comment).delete()
	else:
		return 403
