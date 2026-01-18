from datetime import datetime

from typing import Literal

from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType

from django.db.models import Window
from django.db.models.functions import Rank

from django_comments_xtd.models import XtdComment

from ninja import Router, Schema
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.account.models import Account
from otodb.models import Notification, Subscription
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


class CommentSchema(Schema):
	id: int
	level: int
	user: ProfileSchema
	comment: str
	submit_date: datetime
	parent_id: int
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
	if parent is None or parent.is_removed:
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
