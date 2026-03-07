from datetime import datetime

from typing import Literal

from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.db.models import Window, Case, When, Subquery, OuterRef, F
from django.db.models.functions import Rank

from django_comments_xtd.models import XtdComment

from ninja import Router, Schema
from ninja.pagination import paginate
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.account.models import Account
from otodb.models import Notification, Subscription, RevisionChange
from .common import user_is_trusted, ProfileSchema

comment_router = Router()

models_with_comments = [
	'mediawork',
	'account',
	'pool',
	'tagwork',
	'tagsong',
	'post',
	'bulkrequest',
]


class BaseCommentSchema(Schema):
	id: int
	user: ProfileSchema
	comment: str
	submit_date: datetime


class CommentSchema(BaseCommentSchema):
	parent_id: int
	level: int
	index: int


@comment_router.get('comments', response=list[CommentSchema])
def get(request: HttpRequest, model: Literal[*models_with_comments], pk: int):
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
	model: Literal[*models_with_comments],
	pk: int,
	comment: str,
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
		comment=comment,
		parent_id=parent_id,
	)
	if parent is None:
		Notification.objects.bulk_create(
			[
				Notification(target_id=sub, comment=comment)
				for sub in Subscription.objects.filter(
					entity_type=T, entity_id=pk
				).values_list('subscriber_id', flat=True)
				if sub != request.user.id
			]
		)
		Subscription.objects.get_or_create(
			subscriber=request.user, entity_type=T, entity_id=pk
		)
	else:
		Notification.objects.create(target_id=parent.user_id, comment=comment)
	if model == 'account' and pk != request.user.id:
		Notification.objects.create(target_id=pk, comment=comment)


@comment_router.delete('comment', auth=django_auth)
@user_is_trusted
def delete(
	request: HttpRequest,
	model: Literal[*models_with_comments],
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


class ExtCommentSchema(BaseCommentSchema):
	entity_type: str
	entity_id: str


@comment_router.get('recent', response=list[ExtCommentSchema])
@paginate
def recent(request: HttpRequest):
	return (
		XtdComment.objects.filter(is_removed=False)
		.exclude(content_type__model='post')
		.order_by('-submit_date')
		.annotate(
			entity_id=Case(
				When(
					content_type__model__contains='tag',
					then=Subquery(
						RevisionChange.objects.filter(
							target_type_id=OuterRef('content_type_id'),
							target_id=models.functions.Cast(
								OuterRef('object_pk'),
								output_field=models.BigIntegerField(),
							),
							target_column='slug',
						).values('target_value')[:1]
					),
				),
				When(
					content_type__model='account',
					then=Subquery(
						Account.objects.filter(
							id=models.functions.Cast(
								OuterRef('object_pk'),
								output_field=models.BigIntegerField(),
							),
						).values('username')[:1]
					),
				),
				default=models.functions.Cast(
					F('object_pk'),
					output_field=models.TextField(),
				),
				output_field=models.TextField(),
			),
			entity_type=F('content_type__model'),
		)
	)
