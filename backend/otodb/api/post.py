from datetime import datetime, timezone

from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from ninja import Router, ModelSchema, Schema, Query

from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.common import slugify_tag
from otodb.models import (
	Notification,
	Post,
	PostContent,
	Subscription,
	EntityLink,
)
from otodb.account.models import Account
from otodb.models.enums import PostCategory, LanguageTypes

from .common import (
	AuthedHttpRequest,
	ProfileSchema,
	user_is_trusted,
	restrict_internal,
	EntitySchema,
)

from otodb.discord import discord_post

post_router = Router()


class PostOverviewSchema(ModelSchema):
	id: int
	added_by: ProfileSchema
	modified: datetime
	last_post_by: str | None = None
	last_post_at: datetime | None = None
	entities: list[EntitySchema] = []

	class Meta:
		model = Post
		fields = ['title', 'category', 'closed_at']


class PostContentSchema(ModelSchema):
	class Meta:
		model = PostContent
		fields = ['lang', 'page', 'modified']


class PostSchema(ModelSchema):
	added_by: ProfileSchema
	pages: list[PostContentSchema]
	entities: list[EntitySchema] = []
	edited_by: ProfileSchema | None = None

	class Meta:
		model = Post
		fields = [
			'title',
			'category',
			'edited_at',
			'closed_at',
		]


@post_router.get('post', response=PostSchema)
def post(request: HttpRequest, post_id: int):
	return get_object_or_404(Post, id=post_id)


@post_router.get('categories', response=list[list[PostOverviewSchema]])
def categories(request: HttpRequest):
	return [
		Post.objects.filter(category=i).with_activity()[:5]
		for i, _ in PostCategory.choices
	]


@post_router.get('category', response=list[PostOverviewSchema])
@paginate
def category(request: HttpRequest, category: PostCategory):
	return Post.objects.filter(category=category).with_activity()


class PostInSchema(Schema):
	title: str
	post: str
	category: PostCategory
	lang: LanguageTypes
	target_users: list[str]
	entities: list[EntitySchema]


def get_entity_link_ent(e: EntitySchema):
	obj = (
		ContentType.objects.get(model=e.entity)
		.model_class()
		.objects.get(
			**({'slug': slugify_tag(e.id)} if 'tag' in e.entity else {'id': e.id})
		)
	)
	if hasattr(obj, 'aliased_to') and obj.aliased_to:
		obj = obj.aliased_to
	return obj


@post_router.post('post', response=int, auth=django_auth)
@user_is_trusted
@restrict_internal
@transaction.atomic
def new(request: AuthedHttpRequest, payload: PostInSchema):
	assert payload.category > 0
	assert payload.title
	assert payload.post

	p = Post.objects.create(
		title=payload.title, added_by=request.user, category=payload.category
	)
	PostContent.objects.create(
		post=p,
		lang=payload.lang,
		page=payload.post,
	)
	if payload.entities:
		if payload.category != 3:
			raise HttpError(400, 'Bad Request')
		EntityLink.objects.bulk_create(
			[
				EntityLink(post=p, entity=get_entity_link_ent(e))
				for e in payload.entities
			]
		)

	Notification.objects.bulk_create(
		[
			Notification(target=u, post=p)
			for u in Account.objects.filter(username__in=payload.target_users)
		]
	)

	Subscription.objects.create(subscriber=request.user, entity=p)

	transaction.on_commit(lambda: discord_post.enqueue(p.pk, request.user.username))

	return p.pk


class PostEditSchema(Schema):
	post_id: int
	title: str
	post: str
	lang: LanguageTypes
	entities: list[EntitySchema]


@post_router.put('post', auth=django_auth)
@user_is_trusted
@restrict_internal
@transaction.atomic
def edit(request: HttpRequest, payload: PostEditSchema):
	p = get_object_or_404(Post, id=payload.post_id)
	is_admin = request.user.level >= Account.Levels.ADMIN
	if not is_admin:
		if p.added_by_id != request.user.pk:
			raise HttpError(403, 'Forbidden')
		# Lock: if an admin has edited this post, original author can no longer edit
		if p.edited_by_id and p.edited_by_id != p.added_by_id:
			raise HttpError(403, 'Forbidden')

	now = datetime.now(tz=timezone.utc)
	p.title = payload.title
	p.edited_at = now
	p.edited_by = request.user
	p.save(update_fields=['title', 'edited_at', 'edited_by'])

	if not PostContent.objects.filter(post=p, lang=payload.lang).update(
		page=payload.post
	):
		PostContent.objects.create(post=p, lang=payload.lang, page=payload.post)

	if p.category == 3:
		EntityLink.objects.filter(post=p).delete()
		if payload.entities:
			EntityLink.objects.bulk_create(
				[
					EntityLink(post=p, entity=get_entity_link_ent(e))
					for e in payload.entities
				]
			)


class PostCloseSchema(Schema):
	post_id: int


@post_router.put('close', auth=django_auth)
@transaction.atomic
def close(request: AuthedHttpRequest, payload: PostCloseSchema):
	p = get_object_or_404(Post, id=payload.post_id)
	is_owner = request.user.level >= Account.Levels.OWNER
	is_author = p.added_by_id == request.user.pk
	if not (is_owner or is_author):
		raise HttpError(403, 'Forbidden')

	p.closed_at = datetime.now(tz=timezone.utc)
	p.save(update_fields=['closed_at'])


@post_router.put('unclose', auth=django_auth)
@transaction.atomic
def unclose(request: AuthedHttpRequest, payload: PostCloseSchema):
	p = get_object_or_404(Post, id=payload.post_id)
	is_owner = request.user.level >= Account.Levels.OWNER
	is_author = p.added_by_id == request.user.pk
	if not (is_owner or is_author):
		raise HttpError(403, 'Forbidden')

	p.closed_at = None
	p.save(update_fields=['closed_at'])


@post_router.get('threads', response=list[PostOverviewSchema])
@paginate
def threads(request: HttpRequest, entity: EntitySchema = Query(...)):
	return Post.objects.filter(
		id__in=EntityLink.objects.filter(
			entity_type__model=entity.entity,
			entity_id=get_entity_link_ent(entity).pk,
		).values('post_id')
	).with_activity()


@post_router.get('search', response=list[PostOverviewSchema])
@paginate
def search(
	request: HttpRequest,
	query: str,
	category: PostCategory | None = None,
):
	posts = Post.objects.filter(title__icontains=query).with_activity()
	if category is not None and category >= 0:
		posts = posts.filter(category=category)
	return posts


@post_router.get('recent', response=list[PostOverviewSchema])
@paginate
def recent_posts(request: HttpRequest):
	return Post.objects.with_activity()
