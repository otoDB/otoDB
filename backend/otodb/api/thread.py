import re
from datetime import datetime, timezone
from enum import Enum

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Max
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.account.models import Account
from otodb.common import slugify_tag
from otodb.discord import discord_thread, discord_threadpost
from otodb.models import (
	EntityLink,
	Notification,
	Subscription,
	Thread,
	ThreadPost,
)
from otodb.models.enums import NotificationReason, PostCategory

from .common import (
	AuthedHttpRequest,
	OtodbID,
	ProfileSchema,
	restrict_internal,
	user_is_trusted,
)

thread_router = Router()

POST_REF_RE = re.compile(r'(?<![/\w])t(\d+)\.(\d+)(?!\w)')


class PostEntities(str, Enum):
	WORK = 'mediawork'
	TAG = 'tagwork'
	SONG_ATTRIBUTE = 'tagsong'
	SONG = 'mediasong'
	UPLOAD = 'worksource'
	PROFILE = 'account'


class PostEntitySchema(Schema):
	id: str
	entity: PostEntities


class ThreadOverviewSchema(ModelSchema):
	id: OtodbID
	added_by: ProfileSchema
	modified: datetime
	last_post_by: str | None = None
	last_post_at: datetime | None = None
	post_count: int = 0
	entities: list[PostEntitySchema] = []
	category: PostCategory

	class Meta:
		model = Thread
		fields = ['title', 'closed_at']


class ThreadSchema(ModelSchema):
	id: OtodbID
	added_by: ProfileSchema
	entities: list[PostEntitySchema] = []
	category: PostCategory

	class Meta:
		model = Thread
		fields = ['title', 'closed_at', 'created_at']


class ThreadPostSchema(ModelSchema):
	user: ProfileSchema
	edited_by: ProfileSchema | None = None

	class Meta:
		model = ThreadPost
		fields = ['num', 'body', 'created_at', 'edited_at']


class PostRefSchema(Schema):
	num: int
	user: ProfileSchema


def get_entity_link_ent(e: PostEntitySchema):
	obj = (
		ContentType.objects.get(model=e.entity)
		.model_class()
		.objects.get(
			**(
				{'slug': slugify_tag(e.id)}
				if 'tag' in e.entity
				else {'username__iexact': e.id}
				if e.entity == PostEntities.PROFILE
				else {'id': e.id}
			)
		)
	)
	if hasattr(obj, 'aliased_to') and obj.aliased_to:
		obj = obj.aliased_to
	return obj


@thread_router.get('thread', response=ThreadSchema)
def get_thread(request: HttpRequest, thread_id: OtodbID):
	return get_object_or_404(Thread, id=thread_id, is_removed=False)


@thread_router.get('posts', response=list[ThreadPostSchema])
@paginate
def get_posts(request: HttpRequest, thread_id: OtodbID):
	return (
		ThreadPost.objects.filter(thread_id=thread_id, is_removed=False)
		.select_related('user', 'edited_by')
		.order_by('num')
	)


@thread_router.get('post', response=PostRefSchema)
def get_post(request: HttpRequest, thread_id: OtodbID, num: int):
	return get_object_or_404(ThreadPost, thread_id=thread_id, num=num, is_removed=False)


@thread_router.get('position', response=int)
def position(request: HttpRequest, thread_id: OtodbID, num: int):
	"""1-based index of the post among non-removed posts (ordered by num)."""
	return ThreadPost.objects.filter(
		thread_id=thread_id, is_removed=False, num__lte=num
	).count()


class ThreadInSchema(Schema):
	title: str
	post: str
	category: PostCategory
	target_users: list[str]
	entities: list[PostEntitySchema]


def _add_reference_targets(
	body: str, thread_id: int, reasons: dict[int, NotificationReason]
) -> None:
	"""Notify the authors of *cross-thread* posts referenced via t{id}.{num}.
	Same-thread references need no special handling: those authors posted in the
	thread and are therefore already subscribers."""
	for tid, num in POST_REF_RE.findall(body):
		if int(tid) == thread_id:
			continue
		author_id = (
			ThreadPost.objects.filter(
				thread_id=int(tid), num=int(num), is_removed=False
			)
			.values_list('user_id', flat=True)
			.first()
		)
		if author_id:
			reasons.setdefault(author_id, NotificationReason.MENTION)


def _notify(reasons: dict[int, NotificationReason], post: ThreadPost) -> None:
	"""Create one notification per target user pointing at `post`."""
	reasons.pop(post.user_id, None)
	if reasons:
		Notification.objects.bulk_create(
			[
				Notification(target_id=uid, threadpost=post, reason=reason)
				for uid, reason in reasons.items()
			]
		)


@thread_router.post('thread', response=OtodbID, auth=django_auth)
@user_is_trusted
@restrict_internal
@transaction.atomic
def new_thread(request: AuthedHttpRequest, payload: ThreadInSchema):
	assert payload.category >= 0
	assert payload.title
	assert payload.post

	if payload.category == PostCategory.ANNOUNCEMENT and not request.user.is_admin:
		raise HttpError(403, 'Forbidden')

	t = Thread.objects.create(
		title=payload.title,
		added_by=request.user,
		category=payload.category,
	)
	op = ThreadPost.objects.create(
		thread=t, num=1, user=request.user, body=payload.post
	)
	if payload.entities:
		if payload.category != PostCategory.GARDENING:
			raise HttpError(400, 'Bad Request')
		EntityLink.objects.bulk_create(
			[
				EntityLink(thread=t, entity=get_entity_link_ent(e))
				for e in payload.entities
			]
		)

	reasons: dict[int, NotificationReason] = {}
	if payload.target_users:
		for uid in Account.objects.filter(
			username__in=payload.target_users
		).values_list('id', flat=True):
			reasons[uid] = NotificationReason.MENTION
	if payload.entities:
		usernames = [e.id for e in payload.entities if e.entity == PostEntities.PROFILE]
		for name in usernames:
			if account := Account.objects.filter(username__iexact=name).first():
				reasons[account.id] = NotificationReason.THREAD_LINKED
	_add_reference_targets(payload.post, t.id, reasons)
	_notify(reasons, op)

	Subscription.objects.create(subscriber=request.user, entity=t)

	transaction.on_commit(lambda: discord_thread.enqueue(t.pk, request.user.username))

	return t.pk


class ThreadEditSchema(Schema):
	thread_id: OtodbID
	title: str
	entities: list[PostEntitySchema]


@thread_router.put('thread', auth=django_auth)
@user_is_trusted
@restrict_internal
@transaction.atomic
def edit_thread(request: AuthedHttpRequest, payload: ThreadEditSchema):
	t = get_object_or_404(Thread, id=payload.thread_id, is_removed=False)
	if not request.user.is_mod and t.added_by_id != request.user.pk:
		raise HttpError(403, 'Forbidden')

	t.title = payload.title
	t.save(update_fields=['title'])

	if t.category == PostCategory.GARDENING:
		EntityLink.objects.filter(thread=t).delete()
		if payload.entities:
			EntityLink.objects.bulk_create(
				[
					EntityLink(thread=t, entity=get_entity_link_ent(e))
					for e in payload.entities
				]
			)


class PostInSchema(Schema):
	thread_id: OtodbID
	body: str
	mentioned_users: list[str]


@thread_router.post('post', auth=django_auth, throttle=[AuthRateThrottle('1/8s')])
@user_is_trusted
@restrict_internal
@transaction.atomic
def new_post(request: AuthedHttpRequest, payload: PostInSchema):
	t = get_object_or_404(
		Thread.objects.select_for_update(), id=payload.thread_id, is_removed=False
	)
	if t.closed_at and not request.user.is_mod:
		raise HttpError(403, 'Thread is closed')

	num = (t.posts.aggregate(m=Max('num'))['m'] or 0) + 1
	post = ThreadPost.objects.create(
		thread=t, num=num, user=request.user, body=payload.body
	)

	# Notify thread subscribers (REPLY) and @mentioned users (MENTION).
	reasons: dict[int, NotificationReason] = {}
	ct = ContentType.objects.get_for_model(Thread)
	for uid in (
		Subscription.objects.filter(entity_type=ct, entity_id=t.pk)
		.exclude(subscriber_id=request.user.pk)
		.values_list('subscriber_id', flat=True)
	):
		reasons[uid] = NotificationReason.REPLY
	if payload.mentioned_users:
		for uid in Account.objects.filter(
			username__in=payload.mentioned_users
		).values_list('id', flat=True):
			reasons[uid] = NotificationReason.MENTION
	_add_reference_targets(payload.body, t.id, reasons)
	_notify(reasons, post)

	# Subscribe the replier so they're notified of future activity.
	Subscription.objects.get_or_create(
		subscriber=request.user, entity_type=ct, entity_id=t.pk
	)

	transaction.on_commit(
		lambda: discord_threadpost.enqueue(post.pk, request.user.username)
	)
	return num


class PostEditSchema(Schema):
	thread_id: OtodbID
	num: int
	body: str


@thread_router.put('post', auth=django_auth)
@user_is_trusted
@restrict_internal
def edit_post(request: AuthedHttpRequest, payload: PostEditSchema):
	post = get_object_or_404(
		ThreadPost, thread_id=payload.thread_id, num=payload.num, is_removed=False
	)
	if not request.user.is_mod:
		if post.user_id != request.user.pk:
			raise HttpError(403, 'Forbidden')
		# Lock: if a mod has edited this post, the author can no longer edit.
		if post.edited_by_id and post.edited_by_id != post.user_id:
			raise HttpError(403, 'Forbidden')
		if (
			datetime.now(tz=timezone.utc) - post.created_at
			> settings.OTODB_COMMENT_EDIT_WINDOW
		):
			raise HttpError(403, 'Edit window has passed')
	post.body = payload.body
	post.edited_at = datetime.now(tz=timezone.utc)
	post.edited_by = request.user
	post.save(update_fields=['body', 'edited_at', 'edited_by'])


@thread_router.delete('post', auth=django_auth)
@user_is_trusted
def delete_post(request: AuthedHttpRequest, thread_id: OtodbID, num: int):
	if num == 1:
		raise HttpError(400, 'Cannot delete the opening post')
	post = get_object_or_404(ThreadPost, thread_id=thread_id, num=num)
	if request.user.is_mod or post.user_id == request.user.pk:
		post.is_removed = True
		post.save(update_fields=['is_removed'])
		Notification.objects.filter(threadpost=post).delete()
	else:
		raise HttpError(403, 'Forbidden')


@thread_router.put('close', auth=django_auth)
@transaction.atomic
def toggle_close(request: AuthedHttpRequest, thread_id: OtodbID):
	t = get_object_or_404(Thread, id=thread_id, is_removed=False)
	is_mod = request.user.is_mod
	is_author = t.added_by_id == request.user.pk
	if not t.closed_at:
		if is_mod:
			t.closed_at = datetime.now(tz=timezone.utc)
		else:
			raise HttpError(403, 'Forbidden')
	else:
		if is_mod or is_author:
			t.closed_at = None
		else:
			raise HttpError(403, 'Forbidden')
	t.save(update_fields=['closed_at'])


def _visible_threads():
	return Thread.objects.filter(is_removed=False)


@thread_router.get('categories', response=dict[str, list[ThreadOverviewSchema]])
def categories(request: HttpRequest):
	return {
		str(i): _visible_threads().filter(category=i).with_activity()[:5]
		for i, _ in PostCategory.choices
	}


@thread_router.get('category', response=list[ThreadOverviewSchema])
@paginate
def category(request: HttpRequest, category: PostCategory):
	return _visible_threads().filter(category=category).with_activity()


@thread_router.get('threads', response=list[ThreadOverviewSchema])
@paginate
def threads(request: HttpRequest, entity: PostEntitySchema = Query(...)):
	return (
		_visible_threads()
		.filter(
			id__in=EntityLink.objects.filter(
				entity_type__model=entity.entity,
				entity_id=get_entity_link_ent(entity).pk,
			).values('thread_id')
		)
		.with_activity()
	)


@thread_router.get('search', response=list[ThreadOverviewSchema])
@paginate
def search(
	request: HttpRequest,
	query: str,
	category: PostCategory | None = None,
):
	threads = _visible_threads().filter(title__icontains=query).with_activity()
	if category is not None and category >= 0:
		threads = threads.filter(category=category)
	return threads


@thread_router.get('recent', response=list[ThreadOverviewSchema])
@paginate
def recent_threads(request: HttpRequest):
	return _visible_threads().with_activity()
