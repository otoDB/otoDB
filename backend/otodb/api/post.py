from datetime import datetime, timezone

from django.db import transaction
from django.db.models import (
	Subquery,
	OuterRef,
	DateTimeField,
	CharField,
	F,
	Case,
	When,
	TextField,
	Q,
)
from django.db.models.functions import Greatest, Coalesce, Cast
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from django_comments_xtd.models import XtdComment

from ninja import Router, ModelSchema, Schema, Query
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.common import clean_incoming_slug
from otodb.models import (
	Notification,
	Post,
	PostContent,
	Subscription,
	EntityLink,
	RevisionChange,
)
from otodb.models.tag import OtodbTagModel
from otodb.account.models import Account
from otodb.models.enums import PostCategory, LanguageTypes

from .common import (
	ProfileSchema,
	user_is_trusted,
	restrict_internal,
	EntitySchema,
)

post_router = Router()


class PostOverviewSchema(ModelSchema):
	id: int
	added_by: ProfileSchema
	modified: datetime

	class Meta:
		model = Post
		fields = ['title', 'category']


class PostContentSchema(ModelSchema):
	class Meta:
		model = PostContent
		fields = ['lang', 'page', 'modified']


class PostSchema(ModelSchema):
	added_by: ProfileSchema
	pages: list[PostContentSchema]
	entities: list[EntitySchema] | None = None

	class Meta:
		model = Post
		fields = ['title', 'category']


@post_router.get('post', response=PostSchema)
def post(request: HttpRequest, post_id: int):
	post = get_object_or_404(Post, id=post_id)
	if post.category == 3:
		tag_models = [
			ct.id
			for ct in ContentType.objects.get_for_models(
				*OtodbTagModel.__subclasses__()
			).values()
		]
		post.entities = (
			post.entitylink_set.annotate(
				tg_id=(
					Case(
						When(
							Q(entity_type__id__in=tag_models),
							then=Subquery(
								RevisionChange.objects.filter(
									target_type_id=OuterRef('entity_type_id'),
									target_id=OuterRef('entity_id'),
									target_column='slug',
								).values('target_value')[:1]
							),
						),
						default=Cast(F('entity_id'), output_field=TextField()),
					)
				),
				ent=F('entity_type__model'),
			)
			.values('ent', 'tg_id')
			.annotate(entity=F('ent'), id=F('tg_id'))
		)
	return post


def annotate_modified(qs):
	return qs.annotate(
		modified=Subquery(
			PostContent.objects.filter(post_id=OuterRef('id'))
			.order_by('modified')
			.values('modified')[:1]
		)
	)


@post_router.get('categories', response=list[list[PostOverviewSchema]])
def categories(request: HttpRequest):
	return [
		annotate_modified(Post.objects.filter(category=i)).order_by('-modified')[:5]
		for i, _ in PostCategory.choices
	]


@post_router.get('category', response=list[PostOverviewSchema])
@paginate
def category(request: HttpRequest, category: PostCategory):
	return annotate_modified(Post.objects.filter(category=category)).order_by(
		'-modified'
	)


class PostInSchema(Schema):
	title: str
	post: str
	category: PostCategory
	lang: LanguageTypes
	target_users: list[str]
	entities: list[EntitySchema]


def get_entity_link_ent(e: EntitySchema):
	return (
		ContentType.objects.get(model=e.entity)
		.model_class()
		.objects.get(
			**(
				{'slug': clean_incoming_slug(e.id)}
				if 'tag' in e.entity
				else {'id': e.id}
			)
		)
	)


@post_router.post('post', response=int, auth=django_auth)
@user_is_trusted
@restrict_internal
@transaction.atomic
def new(request: HttpRequest, payload: PostInSchema):
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
	return p.pk


@post_router.get('threads', response=list[PostOverviewSchema])
@paginate
def threads(request: HttpRequest, entity: EntitySchema = Query(...)):
	return annotate_modified(
		Post.objects.filter(
			id__in=EntityLink.objects.filter(
				entity_type__model=entity.entity,
				entity_id=get_entity_link_ent(entity).id,
			).values('post_id')
		)
	)


@post_router.get('search', response=list[PostOverviewSchema])
@paginate
def search(
	request: HttpRequest,
	query: str,
	category: PostCategory | None = None,
):
	posts = annotate_modified(Post.objects.filter(title__icontains=query))
	if category is not None and category >= 0:
		posts = posts.filter(category=category)
	return posts


@post_router.get('recent', response=list[PostOverviewSchema])
@paginate
def recent_posts(request: HttpRequest):
	from django.contrib.contenttypes.models import ContentType

	return Post.objects.annotate(
		modified=Greatest(
			Subquery(
				PostContent.objects.filter(post_id=OuterRef('id'))
				.order_by('modified')
				.values('modified')[:1]
			),
			Coalesce(
				Subquery(
					XtdComment.objects.filter(
						content_type=ContentType.objects.get_for_model(Post),
						object_pk=Cast(OuterRef('id'), CharField()),
					)
					.order_by('submit_date')
					.values('submit_date')[:1]
				),
				datetime.fromtimestamp(0, tz=timezone.utc),
				output_field=DateTimeField(),
			),
		)
	).order_by('-modified')
