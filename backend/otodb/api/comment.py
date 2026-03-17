from datetime import datetime, timezone

from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType

from django.db import models, transaction
from django.db.models import Window, Case, When, Subquery, OuterRef, F
from django.db.models.functions import Rank

from django_comments_xtd.models import XtdComment

from ninja import Router, Schema
from ninja.pagination import paginate
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle
from ninja.errors import HttpError

from otodb.account.models import Account
from otodb.models import Notification, Subscription, RevisionChange, CommentMeta
from .common import AuthedHttpRequest, user_is_trusted, ProfileSchema, restrict_internal
from otodb.discord import discord_comment

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


class BaseCommentSchema(Schema):
	id: int
	user: ProfileSchema
	comment: str
	submit_date: datetime


class CommentSchema(BaseCommentSchema):
	parent_id: int
	level: int
	index: int
	edited_at: datetime | None = None
	edited_by: ProfileSchema | None = None


class CommentInSchema(Schema):
	model: ModelsWithComments
	pk: int
	comment_text: str
	parent_id: int = 0
	mentioned_users: list[str]


@comment_router.get('comments', response=list[CommentSchema])
def get(request: HttpRequest, model: ModelsWithComments, pk: int):
	T = ContentType.objects.get(model=model)
	index = Window(
		expression=Rank(),
		order_by='submit_date',
	)
	result = []
	for c in (
		XtdComment.objects.filter(content_type=T, object_pk=pk)
		.select_related('meta', 'meta__edited_by')
		.order_by('id')
		.annotate(index=index)
	):
		if c.is_removed:
			continue
		try:
			c.edited_at = c.meta.edited_at
			c.edited_by = c.meta.edited_by
		except CommentMeta.DoesNotExist:
			c.edited_at = None
			c.edited_by = None
		result.append(c)
	return result


@comment_router.post('comment', auth=django_auth, throttle=[AuthRateThrottle('1/8s')])
@user_is_trusted
@restrict_internal
def post(
	request: AuthedHttpRequest,
	payload: CommentInSchema,
):
	T = ContentType.objects.get(model=payload.model)
	parent_id = payload.parent_id
	comment_text = payload.comment_text
	pk = payload.pk
	parent = None if parent_id == 0 else XtdComment.objects.get(id=parent_id)
	if parent is not None and parent.is_removed:
		raise HttpError(400, 'Bad Request')

	comment = XtdComment.objects.create(
		content_type=T,
		object_pk=pk,
		site_id=1,
		user=request.user,
		comment=comment_text,
		parent_id=parent_id,
	)
	target_names: set[str] = set()
	if parent is None:
		target_names |= set(
			Subscription.objects.filter(entity_type=T, entity_id=pk)
			.exclude(subscriber_id=request.user.pk)
			.values_list('subscriber__username', flat=True)
		)
		Subscription.objects.get_or_create(
			subscriber=request.user, entity_type=T, entity_id=pk
		)
	else:
		target_names.add(parent.user.username)
	if payload.model == 'account' and pk != request.user.pk:
		target_names.add(Account.objects.get(id=pk).username)

	target_names |= set(payload.mentioned_users)
	target_names.discard(request.user.username)

	Notification.objects.bulk_create(
		[
			Notification(target=u, comment=comment)
			for u in Account.objects.filter(username__in=target_names)
		]
	)

	transaction.on_commit(
		lambda: discord_comment.enqueue(
			comment.pk, payload.model, payload.pk, request.user.username
		)
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
		raise HttpError(403, 'Forbidden')


class CommentEditSchema(Schema):
	comment_id: int
	comment_text: str


@comment_router.put('comment', auth=django_auth)
@user_is_trusted
@restrict_internal
def edit(request: HttpRequest, payload: CommentEditSchema):
	comment = XtdComment.objects.select_related('meta').get(id=payload.comment_id)
	is_admin = request.user.level >= Account.Levels.ADMIN
	if not is_admin:
		if comment.user != request.user:
			raise HttpError(403, 'Forbidden')
		# Lock: if an admin has edited this comment, original author can no longer edit
		try:
			meta = comment.meta
			if meta.edited_by_id and meta.edited_by_id != comment.user_id:
				raise HttpError(403, 'Forbidden')
		except CommentMeta.DoesNotExist:
			pass
		if (
			datetime.now(tz=timezone.utc) - comment.submit_date
			> settings.OTODB_COMMENT_EDIT_WINDOW
		):
			raise HttpError(403, 'Edit window has passed')
	comment.comment = payload.comment_text
	comment.save()
	CommentMeta.objects.update_or_create(
		comment=comment,
		defaults={
			'edited_at': datetime.now(tz=timezone.utc),
			'edited_by': request.user,
		},
	)


class ExtCommentSchema(BaseCommentSchema):
	entity_type: str
	entity_id: str


@comment_router.get('recent', response=list[ExtCommentSchema])
@paginate
def recent(request: HttpRequest):
	return (
		XtdComment.objects.filter(is_removed=False)
		.exclude(content_type__model='post')
		.exclude(content_type__model='account')
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
