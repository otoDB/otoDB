from datetime import datetime, timezone
from enum import Enum

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Case, F, OuterRef, Subquery, When, Window
from django.db.models.functions import Rank
from django.http import HttpRequest
from django_comments_xtd.models import XtdComment
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle
from pydantic import field_validator

from otodb.account.models import Account
from otodb.discord import discord_comment
from otodb.models import CommentMeta, Notification, RevisionChange, Subscription

from .common import AuthedHttpRequest, ProfileSchema, restrict_internal, user_is_trusted

comment_router = Router()


class ModelsWithComments(str, Enum):
	WORK = 'mediawork'
	PROFILE = 'account'
	LIST = 'pool'
	TAG = 'tagwork'
	SONG_ATTRIBUTE = 'tagsong'
	POST = 'post'
	REQUEST = 'bulkrequest'


class BaseCommentSchema(Schema):
	id: str
	user: ProfileSchema
	comment: str
	submit_date: datetime

	@field_validator('id', mode='before')
	@classmethod
	def _coerce_id(cls, v):
		return str(v)


class CommentSchema(BaseCommentSchema):
	parent_id: str
	level: int
	index: int
	edited_at: datetime | None = None
	edited_by: ProfileSchema | None = None

	@field_validator('parent_id', mode='before')
	@classmethod
	def _coerce_parent_id(cls, v):
		return str(v)


class CommentInSchema(Schema):
	model: ModelsWithComments
	pk: str
	comment_text: str
	parent_id: str | None = None
	mentioned_users: list[str]


@comment_router.get('comments', response=list[CommentSchema])
def get(request: HttpRequest, model: ModelsWithComments, pk: str):
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
	parent = None if parent_id is None else XtdComment.objects.get(id=int(parent_id))
	if parent is not None and parent.is_removed:
		raise HttpError(400, 'Bad Request')

	comment = XtdComment.objects.create(
		content_type=T,
		object_pk=pk,
		site_id=1,
		user=request.user,
		comment=comment_text,
		parent_id=int(parent_id) if parent_id is not None else None,
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
	pk: str,
	comment_id: str,
):
	T = ContentType.objects.get(model=model)
	comment = XtdComment.objects.get(
		content_type=T, object_pk=pk, site_id=1, id=int(comment_id)
	)
	if request.user.level >= Account.Levels.ADMIN or comment.user == request.user:
		comment.is_removed = True
		comment.save()
		Notification.objects.filter(comment=comment).delete()
	else:
		raise HttpError(403, 'Forbidden')


class CommentEditSchema(Schema):
	comment_id: str
	comment_text: str


@comment_router.put('comment', auth=django_auth)
@user_is_trusted
@restrict_internal
def edit(request: HttpRequest, payload: CommentEditSchema):
	comment = XtdComment.objects.select_related('meta').get(id=int(payload.comment_id))
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
