from datetime import datetime, timezone

from django.db import transaction
from django.db.models import Subquery, OuterRef, DateTimeField, CharField
from django.db.models.functions import Greatest, Coalesce, Cast
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from django_comments_xtd.models import XtdComment

from ninja import Router, ModelSchema
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import (
	Notification,
	Post,
	PostContent,
	Subscription,
)
from otodb.models.enums import PostCategory, LanguageTypes

from .common import ProfileSchema, user_is_trusted, mentioned_user_ids, render_markdown

post_router = Router()


class PostContentSchema(ModelSchema):
	class Meta:
		model = PostContent
		fields = ['lang', 'page_rendered', 'modified']


class PostSchema(ModelSchema):
	added_by: ProfileSchema
	pages: list[PostContentSchema]

	class Meta:
		model = Post
		fields = ['title', 'category']


class PostOverviewSchema(ModelSchema):
	id: int
	added_by: ProfileSchema
	modified: datetime

	class Meta:
		model = Post
		fields = ['title', 'category']


@post_router.get('post', response=PostSchema)
def post(request: HttpRequest, post_id: int):
	post = get_object_or_404(Post, id=post_id)
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


@post_router.post('post', response=int, auth=django_auth)
@user_is_trusted
@transaction.atomic
def new(
	request: HttpRequest,
	title: str,
	post: str,
	category: PostCategory,
	lang: LanguageTypes,
):
	assert category > 0
	assert title
	assert post
	rendered_post = render_markdown(post)
	target_ids = mentioned_user_ids(post, exclude_user_id=request.user.pk)

	p = Post.objects.create(title=title, added_by=request.user, category=category)
	PostContent.objects.create(
		post=p,
		lang=lang,
		page=post,
		page_rendered=rendered_post,
	)

	Notification.objects.bulk_create(
		[Notification(target_id=target_id, post=p) for target_id in target_ids]
	)

	Subscription.objects.create(subscriber=request.user, entity=p)
	return p.pk


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
