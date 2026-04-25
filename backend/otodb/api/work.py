from functools import reduce
from typing import List, Literal

from django.conf import settings
from django.db import transaction
from django.db.models import (
	Case,
	Count,
	IntegerField,
	OuterRef,
	Q,
	Subquery,
	Value,
	When,
)
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Schema
from ninja.pagination import paginate
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.account.models import Account
from otodb.common import (
	slugify_tag,
)
from otodb.models import (
	MediaWork,
	ModerationEvent,
	TagWork,
	TagWorkInstance,
	WorkRelation,
	WorkSource,
)
from otodb.models.enums import (
	ErrorCode,
	FlagStatus,
	ModerationAction,
	ModerationEventType,
	ModQueueCategory,
	Platform,
	Rating,
	Route,
	Status,
	WorkTagCategory,
)
from otodb.tasks import (
	enqueue_deferred,
	resolve_expired_appeal,
	resolve_expired_flag,
	resolve_expired_work,
)

from .common import (
	ApiError,
	AuthedHttpRequest,
	CreateWorkPayload,
	Error,
	RouterWithRevision,
	SlimWorkSchema,
	TagWorkInstanceInSchema,
	TagWorkInstanceSchema,
	ThinWorkSchema,
	WorkRelationSchema,
	WorkSchema,
	WorkSourceSchema,
	ensure_can_moderate,
	post_relations,
	user_is_editor,
	user_is_staff,
	user_is_trusted,
	with_revision_route,
)

work_router = RouterWithRevision()


class ExternalQuery(Schema):
	work_id: int
	tags: List[TagWorkInstanceSchema]


def _resolve_and_apply_tags(work, payload: list[TagWorkInstanceInSchema]):
	tags = []
	for t in payload:
		try:
			tag = TagWork.objects.get(slug=slugify_tag(t.nameslug))
			tags.append(tag.aliased_to if tag.aliased_to else tag)
		except TagWork.DoesNotExist:
			tags.append(TagWork.objects.create(name=t.nameslug))

	for tag, p in zip(tags, payload):
		changes = {}
		if p.sample is not None and tag.category in [
			WorkTagCategory.CREATOR,
			WorkTagCategory.MEDIA,
			WorkTagCategory.SONG,
		]:
			changes['used_as_source'] = p.sample
		if p.roles and tag.category == WorkTagCategory.CREATOR:
			changes['creator_roles'] = reduce(int.__or__, p.roles)

		TagWorkInstance.objects.update_or_create(
			work=work, work_tag=tag, defaults=changes
		)

	return tags


@work_router.get('query_external', response=ExternalQuery)
def query_external(
	request: AuthedHttpRequest,
	url: str | None = None,
	platform: str | None = None,
	id: str | None = None,
):
	if url:
		work = get_object_or_404(WorkSource.objects, url=url)
	elif platform and id:
		work = get_object_or_404(
			WorkSource.objects.filter(platform=Platform.from_str(platform)),
			Q(source_id=id) | Q(url__endswith=id),
		)
	else:
		raise ValueError(
			"Either 'url' or both 'platform' and 'id' parameters must be provided"
		)

	return {'tags': work.media.tags_annotated, 'work_id': work.media.id}


@work_router.get('search', response=List[ThinWorkSchema], exclude_none=True)
@paginate
def search(
	request: AuthedHttpRequest,
	query: str,
	tags: str | None = None,
	order: Literal['id', '-id', 'pub', '-pub'] | None = '-id',
	queue: Literal['unseen', 'all'] | None = None,
):
	# Silently ignore queue param for non-editors
	if queue is not None and (
		not request.user.is_authenticated or not request.user.is_editor
	):
		queue = None

	search_id = int(query) if query.isdigit() else -1
	if query:
		q = (
			Q(title__icontains=query)
			| Q(description__icontains=query)
			| Q(worksource__title__icontains=query)
		)
	else:
		q = Q()
	if tags:
		for tag in tags.split():
			try:
				match tag[0]:
					case '-' | '+' | '!':
						t = TagWork.objects.get(slug=slugify_tag(tag[1:]))
						if t.aliased_to:
							t = t.aliased_to

						if tag[0] == '-':
							q = q & ~Q(tags=t)
						else:
							children = t.get_descendants()
							sub_q = Q(tags=t)
							for tt in children:
								sub_q = sub_q | Q(tags=tt)

							match tag[0]:
								case '+':  # +: Include subtree
									q = q & sub_q
								case '!':  # !: Exclude subtree
									q = q & ~sub_q
					case _:
						t = TagWork.objects.get(slug=slugify_tag(tag))
						if t.aliased_to:
							t = t.aliased_to

						q = q & Q(tags=t)
			except TagWork.DoesNotExist:
				return []
	elif query:
		q = q | Q(worksource__source_id=query)
		if query.startswith('https'):
			q = q | Q(worksource__url=query)
		if search_id > 0:
			q = q | Q(id=search_id)

	if queue is not None:
		pending = MediaWork.active_objects.filter(status=Status.PENDING)
		pending_flag_or_appeal_ids = ModerationEvent.objects.filter(
			event_type__in=[ModerationEventType.FLAG, ModerationEventType.APPEAL],
			status=FlagStatus.PENDING,
		).values_list('work_id', flat=True)
		queue_q = Q(id__in=pending) | Q(id__in=pending_flag_or_appeal_ids)
		if queue == 'unseen':
			queue_q = queue_q & ~Q(
				moderation_events__event_type=ModerationEventType.DISAPPROVAL,
				moderation_events__by=request.user,
			)
		qs = MediaWork.active_objects.filter(queue_q).filter(q)
	else:
		qs = MediaWork.active_objects.filter(q).visible()

	qs = qs.annotate(
		pub=Subquery(
			WorkSource.objects.filter(media_id=OuterRef('id'))
			.order_by('published_date')
			.values('published_date')[:1]
		),
	)

	if query:
		qs = qs.annotate(
			priority=Case(
				When(id=search_id, then=Value(0)),
				When(worksource__url=query, then=Value(1)),
				When(worksource__source_id=query, then=Value(2)),
				When(title__icontains=query, then=Value(100)),
				When(worksource__title__icontains=query, then=Value(101)),
				When(description__icontains=query, then=Value(102)),
				default=Value(1000),
				output_field=IntegerField(),
			),
		).order_by('priority', order)
	else:
		qs = qs.order_by(order)

	return qs.distinct()


@work_router.get('tags_needed', response=List[ThinWorkSchema], exclude_none=True)
@paginate
def tags_needed(request: AuthedHttpRequest):
	return (
		MediaWork.active_objects.visible()
		.annotate(ntags=Count('tags', filter=Q(tags__deprecated=False)))
		.filter(ntags__lte=4)
		.order_by('ntags')
		.distinct()
	)


@work_router.get('work', response=WorkSchema)
def work(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.objects.with_pending_moderation(), id=work_id)

	is_editor = (
		request.user.is_authenticated and request.user.level >= Account.Levels.EDITOR
	)
	if work.pending_flag:
		is_own = (
			request.user.is_authenticated and work.pending_flag.by_id == request.user.pk
		)
		if not is_editor and not is_own:
			work.pending_flag.by_id = None

	return work


@work_router.delete('work', auth=django_auth)
@user_is_staff
@with_revision_route(Route.MEDIAWORK_DELETE)
def delete_work(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	work.worksource_set.update(media=None)
	work.delete()


@work_router.put('set_tags', auth=django_auth)
@user_is_trusted
@with_revision_route(Route.MEDIAWORK_SET_TAGS)
def set_tags(
	request: AuthedHttpRequest, work_id: int, payload: list[TagWorkInstanceInSchema]
):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	tags = _resolve_and_apply_tags(work, payload)
	work.tags.remove(*work.tags.exclude(id__in=[t.id for t in tags]))
	return 200


@work_router.get('random', response=list[ThinWorkSchema], exclude_none=True)
def random(request: AuthedHttpRequest, n: int = 1):
	return (
		MediaWork.active_objects.visible()
		.filter(rating=Rating.GENERAL)
		.order_by('?')[: min(n, 20)]
	)


@work_router.get('recent', response=list[ThinWorkSchema], exclude_none=True)
def recent(request: AuthedHttpRequest, n: int = 1):
	return MediaWork.active_objects.visible().order_by('-id')[: min(n, 20)]


@work_router.get(
	'relations', response=tuple[list[WorkRelationSchema], list[SlimWorkSchema]]
)
def relations(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	relations = WorkRelation.get_component(work.id)
	return 200, (relations, {w.id: w for r in relations for w in (r.A, r.B)}.values())


@work_router.post('relation', auth=django_auth)
@user_is_trusted
@with_revision_route(Route.WORKRELATION_CREATE)
def relation(
	request: AuthedHttpRequest, this_id: int, payload: list[WorkRelationSchema]
):
	post_relations(MediaWork, this_id, payload)


class WorkEditSchema(ModelSchema):
	class Meta:
		model = MediaWork
		fields = ['title', 'description', 'thumbnail_source', 'rating']


@work_router.post('merge', auth=django_auth)
@user_is_editor
@with_revision_route(Route.MEDIAWORK_MERGE)
def merge_works(
	request: AuthedHttpRequest,
	from_work_id: int,
	to_work_id: int,
	payload: WorkEditSchema,
):
	MediaWork.merge(
		to_work=get_object_or_404(MediaWork.active_objects, id=to_work_id),
		from_work=get_object_or_404(MediaWork.active_objects, id=from_work_id),
		title=payload.title,
		description=payload.description,
		thumbnail_source=get_object_or_404(
			WorkSource.objects, id=payload.thumbnail_source
		),
		rating=payload.rating,
	)
	return


@work_router.put('work', auth=django_auth)
@user_is_trusted
@with_revision_route(Route.MEDIAWORK_UPDATE)
def update_work(
	request: AuthedHttpRequest, work_id: int, payload: WorkEditSchema, reason: str
):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	for attr, value in payload.dict().items():
		if attr == 'thumbnail_source' and value is not None:
			value = get_object_or_404(WorkSource.objects, id=value)
		# Special handling for title: if current is NULL and new is blank, keep NULL
		if attr == 'title' and work.title is None and value == '':
			continue
		setattr(work, attr, value)
	work.save()
	return


@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	return work.worksource_set


@work_router.post('create', auth=django_auth, response={200: int, 409: Error})
@user_is_trusted
@transaction.atomic
@with_revision_route(Route.MEDIAWORK_CREATE)
def create_work(request: AuthedHttpRequest, payload: CreateWorkPayload):
	"""Creates a MediaWork from a source with user-chosen metadata and tags."""
	src = get_object_or_404(WorkSource.objects, id=payload.source_id)
	if src.media is not None:
		raise ApiError(409, ErrorCode.SOURCE_HAS_WORK)

	is_editor = request.user.level >= Account.Levels.EDITOR

	# Upload limit check (members only)
	if not is_editor:
		pending_uploads = (
			MediaWork.active_objects.filter(
				worksource__added_by=request.user,
				status=Status.PENDING,
			)
			.exclude(
				moderation_events__event_type=ModerationEventType.APPEAL,
				moderation_events__status=FlagStatus.PENDING,
			)
			.distinct()
			.count()
		)
		pending_appeals = ModerationEvent.objects.filter(
			event_type=ModerationEventType.APPEAL,
			by=request.user,
			status=FlagStatus.PENDING,
		).count()
		total_slots_used = pending_uploads + (pending_appeals * 3)
		if total_slots_used >= settings.OTODB_MAX_PENDING_WORKS:
			raise ApiError(429, ErrorCode.NO_MORE_UPLOAD_SLOTS)

	work = MediaWork.objects.create(
		title=payload.title or src.title,
		description=payload.description or src.description,
		thumbnail_source=src,
		rating=payload.rating,
		status=Status.PENDING if not is_editor else Status.APPROVED,
	)
	_resolve_and_apply_tags(work, payload.tags)

	if work.status == Status.PENDING:
		transaction.on_commit(
			lambda: enqueue_deferred(
				resolve_expired_work, work.pk, delay=settings.OTODB_MODERATION_PERIOD
			)
		)

	src.media = work
	src.save()

	# Pool assignments
	for pool in src.pool_set.all():
		pool.add_work(work.pk)
		pool.pending_items.remove(src)

	return work.pk


def resolve_work(work: MediaWork):
	"""Resolve a work's pending state and dismiss any pending flags/appeals."""
	work.moderation_events.filter(
		event_type__in=[ModerationEventType.FLAG, ModerationEventType.APPEAL],
		status=FlagStatus.PENDING,
	).update(status=FlagStatus.REJECTED)
	work.status = Status.UNAPPROVED
	work.save(update_fields=['status'])


@work_router.post('approve', auth=django_auth, response={200: None, 403: Error})
@user_is_editor
def approve_work(request: AuthedHttpRequest, work_id: int):
	"""Approve a pending or flagged work, making it active."""
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	ensure_can_moderate(request.user, work)

	work.status = Status.APPROVED
	work.save(update_fields=['status'])

	work.moderation_events.filter(
		event_type=ModerationEventType.FLAG, status=FlagStatus.PENDING
	).update(status=FlagStatus.REJECTED)
	work.moderation_events.filter(
		event_type=ModerationEventType.APPEAL, status=FlagStatus.PENDING
	).update(status=FlagStatus.SUCCEEDED)
	work.moderation_events.filter(event_type=ModerationEventType.DISAPPROVAL).delete()

	ModerationEvent.objects.create(
		work=work, event_type=ModerationEventType.APPROVAL, by=request.user
	)


@work_router.post('disapprove', auth=django_auth, response={200: None, 403: Error})
@user_is_editor
def disapprove_work(request: AuthedHttpRequest, work_id: int, reason: str):
	"""Record that a user reviewed a work and chose not to approve it."""
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	ensure_can_moderate(request.user, work)
	ModerationEvent.objects.update_or_create(
		work=work,
		by=request.user,
		event_type=ModerationEventType.DISAPPROVAL,
		defaults={'reason': reason},
	)


@work_router.post('resolve', auth=django_auth)
@user_is_staff
def resolve_work_admin(request: AuthedHttpRequest, work_id: int):
	"""Immediate resolution by staff - same as expiry, skips the waiting period."""
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	resolve_work(work)
	ModerationEvent.objects.create(
		work=work,
		event_type=ModerationEventType.MOD_ACTION,
		status=ModerationAction.WORK_DELISTED,
		by=request.user,
	)


@work_router.post(
	'flag',
	auth=django_auth,
	throttle=[AuthRateThrottle(f'{settings.OTODB_MAX_FLAGGED_WORKS}/h')],
	response={200: None, 400: Error, 429: Error},
)
@user_is_trusted
def flag_work(request: AuthedHttpRequest, work_id: int, reason: str):
	"""Flag an active work for re-review."""
	work = get_object_or_404(MediaWork.active_objects, id=work_id)

	if work.status != Status.APPROVED:
		raise ApiError(400, ErrorCode.FLAG_NOT_APPROVED)
	if work.moderation_events.filter(
		event_type=ModerationEventType.FLAG, status=FlagStatus.PENDING
	).exists():
		raise ApiError(400, ErrorCode.FLAG_PENDING_FLAG)
	if work.moderation_events.filter(
		event_type=ModerationEventType.APPEAL, status=FlagStatus.PENDING
	).exists():
		raise ApiError(400, ErrorCode.FLAG_PENDING_APPEAL)

	is_editor = request.user.level >= Account.Levels.EDITOR
	if not is_editor:
		active_flags = ModerationEvent.objects.filter(
			event_type=ModerationEventType.FLAG,
			by=request.user,
			status=FlagStatus.PENDING,
		).count()
		if active_flags >= settings.OTODB_MAX_FLAGGED_WORKS:
			raise ApiError(429, ErrorCode.FLAG_LIMIT_REACHED)

	flag = ModerationEvent.objects.create(
		work=work,
		event_type=ModerationEventType.FLAG,
		by=request.user,
		reason=reason,
		status=FlagStatus.PENDING,
	)

	transaction.on_commit(
		lambda: enqueue_deferred(
			resolve_expired_flag, flag.pk, delay=settings.OTODB_MODERATION_PERIOD
		)
	)


@work_router.post(
	'appeal',
	auth=django_auth,
	throttle=[AuthRateThrottle(f'{settings.OTODB_MAX_PENDING_WORKS}/h')],
	response={200: None, 400: Error, 429: Error},
)
@user_is_trusted
def appeal_work(request: AuthedHttpRequest, work_id: int, reason: str):
	"""Appeal an unapproved work to send it back to the mod queue."""
	work = get_object_or_404(
		MediaWork.objects.filter(status=Status.UNAPPROVED), id=work_id
	)
	if work.moderation_events.filter(
		event_type=ModerationEventType.APPEAL, status=FlagStatus.PENDING
	).exists():
		raise ApiError(400, ErrorCode.APPEAL_PENDING)

	is_editor = request.user.level >= Account.Levels.EDITOR
	if not is_editor:
		pending_uploads = (
			MediaWork.active_objects.filter(
				worksource__added_by=request.user,
				status=Status.PENDING,
			)
			.exclude(
				moderation_events__event_type=ModerationEventType.APPEAL,
				moderation_events__status=FlagStatus.PENDING,
			)
			.distinct()
			.count()
		)
		pending_appeals = ModerationEvent.objects.filter(
			event_type=ModerationEventType.APPEAL,
			by=request.user,
			status=FlagStatus.PENDING,
		).count()
		total_slots_used = pending_uploads + (pending_appeals * 3)
		if total_slots_used + 3 > settings.OTODB_MAX_PENDING_WORKS:
			raise ApiError(429, ErrorCode.NO_MORE_APPEAL_SLOTS)

	appeal = ModerationEvent.objects.create(
		work=work,
		event_type=ModerationEventType.APPEAL,
		by=request.user,
		reason=reason,
		status=FlagStatus.PENDING,
	)

	transaction.on_commit(
		lambda: enqueue_deferred(
			resolve_expired_appeal, appeal.pk, delay=settings.OTODB_MODERATION_PERIOD
		)
	)


@work_router.get('queue', auth=django_auth, response=List[ThinWorkSchema])
@user_is_editor
@paginate
def mod_queue(
	request: AuthedHttpRequest,
	mode: str = 'unseen',
	category: ModQueueCategory | None = None,
):
	"""List works pending moderation: pending, flagged, or appealed."""
	base = MediaWork.active_objects.all()

	def pending_event_work_ids(event_type):
		return ModerationEvent.objects.filter(
			event_type=event_type, status=FlagStatus.PENDING
		).values_list('work_id', flat=True)

	if category == ModQueueCategory.PENDING:
		qs = base.filter(status=Status.PENDING)
	elif category == ModQueueCategory.FLAGGED:
		qs = base.filter(id__in=pending_event_work_ids(ModerationEventType.FLAG))
	elif category == ModQueueCategory.APPEALED:
		qs = base.filter(id__in=pending_event_work_ids(ModerationEventType.APPEAL))
	else:
		pending = base.filter(status=Status.PENDING)
		pending_flag_or_appeal_ids = ModerationEvent.objects.filter(
			event_type__in=[ModerationEventType.FLAG, ModerationEventType.APPEAL],
			status=FlagStatus.PENDING,
		).values_list('work_id', flat=True)
		qs = base.filter(
			Q(id__in=pending) | Q(id__in=pending_flag_or_appeal_ids)
		).distinct()

	if mode == 'unseen':
		qs = qs.exclude(
			moderation_events__event_type=ModerationEventType.DISAPPROVAL,
			moderation_events__by=request.user,
		)

	return qs.order_by('-id')


@work_router.get('similar', response=List[ThinWorkSchema])
def similar(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	wt = work.tags.filter(deprecated=False).values_list('id', flat=True)
	return (
		MediaWork.active_objects.visible()
		.exclude(id=work_id)
		.filter(tags__in=Subquery(wt))
		.annotate(shared_tags_count=Count('tags', filter=Q(tags__in=Subquery(wt))))
		.order_by('-shared_tags_count')
	)[:6]
