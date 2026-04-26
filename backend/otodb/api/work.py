from functools import reduce
from typing import List

import lark
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import (
	Case,
	CharField,
	Count,
	Exists,
	F,
	IntegerField,
	OuterRef,
	Q,
	Subquery,
	Value,
	When,
)
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django_comments_xtd.models import XtdComment
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
	RevisionChange,
	TagWork,
	TagWorkInstance,
	WorkRelation,
	WorkSource,
)
from otodb.models.enums import (
	ErrorCode,
	FlagStatus,
	MediaType,
	ModerationAction,
	ModerationEventType,
	ModQueueCategory,
	OtodbIntegerEnum,
	Platform,
	Rating,
	Role,
	Route,
	Status,
	WorkOrigin,
	WorkRelationTypes,
	WorkStatus,
	WorkTagCategory,
)
from otodb.tasks import (
	enqueue_deferred,
	resolve_expired_appeal,
	resolve_expired_flag,
	resolve_expired_work,
)

from .common import (
	AbstractTagTransformer,
	ApiError,
	AuthedHttpRequest,
	BitmaskAttr,
	BoolAttr,
	CreateWorkPayload,
	Error,
	MetatagSpec,
	OrderEnum,
	RouterWithRevision,
	SlimWorkSchema,
	TagWorkInstanceInSchema,
	TagWorkInstanceSchema,
	ThinWorkSchema,
	WorkRelationSchema,
	WorkSchema,
	WorkSourceSchema,
	count_predicate_q,
	ensure_can_moderate,
	get_search_grammar,
	make_range_metatag,
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


_WORK_TAG_CATEGORY_METATAGS = {
	'eventtags': WorkTagCategory.EVENT,
	'creatortags': WorkTagCategory.CREATOR,
	'mediatags': WorkTagCategory.MEDIA,
	'sourcetags': WorkTagCategory.SOURCE,
	'songtags': WorkTagCategory.SONG,
	'gentags': WorkTagCategory.GENERAL,
	'metatags': WorkTagCategory.META,
	'uncattags': WorkTagCategory.UNCATEGORIZED,
}


class WorkOrder(OtodbIntegerEnum):
	RANDOM = -1, 'random'
	ID = 0, 'id'
	ID_DESC = 1, 'id_desc'
	SUBMITTED = 2, 'submitted'
	SUBMITTED_ASC = 3, 'submitted_asc'
	PUBLISHED = 4, 'published'
	PUBLISHED_ASC = 5, 'published_asc'
	COMMENT = 6, 'comment'
	COMMENT_ASC = 7, 'comment_asc'
	RESOLUTION = 8, 'resolution'
	RESOLUTION_ASC = 9, 'resolution_asc'
	DURATION = 10, 'duration'
	DURATION_ASC = 11, 'duration_asc'


def _resolve_work_order(v: WorkOrder) -> tuple[dict, Q, tuple[str, ...]]:
	match v:
		case WorkOrder.ID:
			return {}, Q(), ('id',)
		case WorkOrder.ID_DESC:
			return {}, Q(), ('-id',)
		case WorkOrder.SUBMITTED:
			return {}, Q(), ('-created_at',)
		case WorkOrder.SUBMITTED_ASC:
			return {}, Q(), ('created_at',)
		case WorkOrder.PUBLISHED | WorkOrder.PUBLISHED_ASC:
			ann = {
				'_pub': Subquery(
					WorkSource.objects.filter(media_id=OuterRef('id'))
					.order_by('published_date')
					.values('published_date')[:1]
				)
			}
			field = '-_pub' if v is WorkOrder.PUBLISHED else '_pub'
			return ann, Q(), (field,)
		case WorkOrder.RESOLUTION | WorkOrder.RESOLUTION_ASC:
			ann = {
				'_mpixels': Subquery(
					WorkSource.objects.filter(media_id=OuterRef('id'))
					.annotate(_mp=F('work_width') * F('work_height'))
					.order_by(F('_mp').desc(nulls_last=True))
					.values('_mp')[:1]
				)
			}
			field = '-_mpixels' if v is WorkOrder.RESOLUTION else '_mpixels'
			return ann, Q(_mpixels__isnull=False), (field,)
		case WorkOrder.DURATION | WorkOrder.DURATION_ASC:
			ann = {
				'_duration': Subquery(
					WorkSource.objects.filter(media_id=OuterRef('id'))
					.order_by(F('work_duration').desc(nulls_last=True))
					.values('work_duration')[:1]
				)
			}
			field = '-_duration' if v is WorkOrder.DURATION else '_duration'
			return ann, Q(_duration__isnull=False), (field,)
		case WorkOrder.COMMENT | WorkOrder.COMMENT_ASC:
			ann = {
				'_last_comment': Subquery(
					XtdComment.objects.filter(
						content_type=ContentType.objects.get_for_model(MediaWork),
						object_pk=Cast(OuterRef('id'), CharField()),
						is_removed=False,
					)
					.order_by('-submit_date')
					.values('submit_date')[:1]
				)
			}
			field = '-_last_comment' if v is WorkOrder.COMMENT else '_last_comment'
			return ann, Q(_last_comment__isnull=False), (field,)
		case WorkOrder.RANDOM:
			return {}, Q(), ('?',)
		case _:
			raise ValueError(f'unrecognized WorkOrder: {v!r}')


def _user_to_q(username):
	"""Match works whose 'first user' is `username`.

	The first user is the author of the earliest non-admin revision targeting
	the work; for works with no non-admin revisions (e.g. those created before
	the revision model existed) it falls back to a `WorkSource.added_by` match.
	"""
	mediawork_ct = ContentType.objects.get_for_model(MediaWork)
	non_admin_rev = RevisionChange.objects.filter(
		target_type=mediawork_ct,
		rev__user__level__lt=Account.Levels.ADMIN,
	)
	first_rev_pks = (
		non_admin_rev.order_by('target_id', 'rev__date')
		.distinct('target_id')
		.values('pk')
	)
	rev_match_ids = RevisionChange.objects.filter(
		pk__in=first_rev_pks, rev__user__username__iexact=username
	).values('target_id')
	src_match_ids = (
		WorkSource.objects.filter(
			added_by__username__iexact=username, media_id__isnull=False
		)
		.exclude(media_id__in=non_admin_rev.values('target_id'))
		.values('media_id')
	)
	return Q(id__in=rev_match_ids) | Q(id__in=src_match_ids)


work_metatag_grammars = {
	'rating': MetatagSpec(Rating, lambda v: Q(rating=v)),
	'status': MetatagSpec(Status, lambda v: Q(status=v)),
	'availability': MetatagSpec(
		WorkStatus,
		lambda v: Exists(
			WorkSource.objects.filter(media_id=OuterRef('id'), work_status=v)
		),
	),
	'platform': MetatagSpec(
		Platform,
		lambda v: Exists(
			WorkSource.objects.filter(media_id=OuterRef('id'), platform=v)
		),
	),
	'origin': MetatagSpec(
		WorkOrigin,
		lambda v: Exists(
			WorkSource.objects.filter(media_id=OuterRef('id'), work_origin=v)
		),
	),
	'user': MetatagSpec(str, _user_to_q),
	'id': MetatagSpec(int, make_range_metatag('id')),
	'width': MetatagSpec(
		int,
		make_range_metatag('work_width', model=WorkSource, fk_field='media_id'),
	),
	'height': MetatagSpec(
		int,
		make_range_metatag('work_height', model=WorkSource, fk_field='media_id'),
	),
	'duration': MetatagSpec(
		int,
		make_range_metatag('work_duration', model=WorkSource, fk_field='media_id'),
	),
	'sources': MetatagSpec(
		int,
		make_range_metatag(model=WorkSource, fk_field='media_id', count=True),
	),
	'origins': MetatagSpec(
		int,
		make_range_metatag(
			model=WorkSource,
			fk_field='media_id',
			count=True,
			work_origin=WorkOrigin.AUTHOR,
		),
	),
	'reuploads': MetatagSpec(
		int,
		make_range_metatag(
			model=WorkSource,
			fk_field='media_id',
			count=True,
			work_origin=WorkOrigin.REUPLOAD,
		),
	),
	'available_sources': MetatagSpec(
		int,
		make_range_metatag(
			model=WorkSource,
			fk_field='media_id',
			count=True,
			work_status=WorkStatus.AVAILABLE,
		),
	),
	'available_origins': MetatagSpec(
		int,
		make_range_metatag(
			model=WorkSource,
			fk_field='media_id',
			count=True,
			work_origin=WorkOrigin.AUTHOR,
			work_status=WorkStatus.AVAILABLE,
		),
	),
	'available_reuploads': MetatagSpec(
		int,
		make_range_metatag(
			model=WorkSource,
			fk_field='media_id',
			count=True,
			work_origin=WorkOrigin.REUPLOAD,
			work_status=WorkStatus.AVAILABLE,
		),
	),
	'comments': MetatagSpec(
		int,
		lambda op, value: count_predicate_q(
			XtdComment.objects.filter(
				content_type=ContentType.objects.get_for_model(MediaWork),
				object_pk=Cast(OuterRef('id'), CharField()),
				is_removed=False,
			),
			op,
			value,
		),
	),
	'mediatype': MetatagSpec(
		MediaType,
		lambda v: Exists(
			TagWorkInstance.objects.filter(
				work_id=OuterRef('id'),
				work_tag__category=WorkTagCategory.MEDIA,
			)
			.annotate(_mt=F('work_tag__media_type').bitand(int(v)))
			.filter(_mt__gt=0)
		),
	),
	'role': MetatagSpec(
		Role,
		lambda v: Exists(
			TagWorkInstance.objects.filter(
				work_id=OuterRef('id'),
				work_tag__category=WorkTagCategory.CREATOR,
			)
			.annotate(_r=F('creator_roles').bitand(int(v)))
			.filter(_r__gt=0)
		),
	),
	'tagcount': MetatagSpec(
		int,
		make_range_metatag(model=TagWorkInstance, fk_field='work_id', count=True),
	),
	**{
		name: MetatagSpec(
			int,
			make_range_metatag(
				model=TagWorkInstance,
				fk_field='work_id',
				count=True,
				work_tag__category=cat,
			),
		)
		for name, cat in _WORK_TAG_CATEGORY_METATAGS.items()
	},
	'relations': MetatagSpec(
		int,
		lambda op, value: count_predicate_q(
			WorkRelation.objects.filter(
				Q(A_id=OuterRef('id')) | Q(B_id=OuterRef('id'))
			),
			op,
			value,
		),
	),
	'relation': MetatagSpec(
		WorkRelationTypes,
		lambda v: Exists(
			WorkRelation.objects.filter(
				Q(A_id=OuterRef('id')) | Q(B_id=OuterRef('id')), relation=v
			)
		),
	),
	**{
		name: MetatagSpec(
			int,
			lambda op, value, r=rel_type: Exists(
				WorkRelation.objects.filter(
					Q(A_id=OuterRef('id')) & Q(**{f'B__id__{op}': value})
					| Q(B_id=OuterRef('id')) & Q(**{f'A__id__{op}': value}),
					relation=r,
				)
			),
		)
		for name, rel_type in {
			'sequel': WorkRelationTypes.SEQUEL,
			'sample': WorkRelationTypes.SAMPLE,
			'respect': WorkRelationTypes.RESPECT,
			'collab': WorkRelationTypes.COLLAB_PART,
		}.items()
	},
	**{
		name: MetatagSpec(
			int,
			make_range_metatag(
				model=WorkRelation,
				fk_field=fk_field,
				count=True,
				relation=rel_type,
			),
		)
		for name, (fk_field, rel_type) in {
			'sequels': ('A_id', WorkRelationTypes.SEQUEL),
			'prequels': ('B_id', WorkRelationTypes.SEQUEL),
			'samples': ('A_id', WorkRelationTypes.SAMPLE),
			'sampled_by': ('B_id', WorkRelationTypes.SAMPLE),
			'respects': ('A_id', WorkRelationTypes.RESPECT),
			'respected_by': ('B_id', WorkRelationTypes.RESPECT),
			'collabs': ('A_id', WorkRelationTypes.COLLAB_PART),
			'collab_parts': ('B_id', WorkRelationTypes.COLLAB_PART),
		}.items()
	},
	'order': MetatagSpec(OrderEnum(WorkOrder), _resolve_work_order),
}
work_search_grammar = get_search_grammar(work_metatag_grammars)


class WorkTagTransformer(AbstractTagTransformer):
	TagModel = TagWork
	TagInstanceModel = TagWorkInstance
	tag_join_name = 'work_tag'
	tagged_join_name = 'work'
	metatag_grammars = work_metatag_grammars
	attribute_handlers = {
		'source': BoolAttr('used_as_source'),
		'role': BitmaskAttr('creator_roles', Role),
	}


@work_router.get('search', response=List[ThinWorkSchema], exclude_none=True)
@paginate
def search(
	request: AuthedHttpRequest,
	query: str,
	tags: str | None = None,
):
	search_id = int(query) if query.isdigit() else -1
	if query:
		q = (
			Q(title__icontains=query)
			| Q(description__icontains=query)
			| Q(worksource__title__icontains=query)
		)
	else:
		q = Q()

	uses_status_metatag = False
	tag_orderings: list = []
	if tags:
		try:
			parsed = work_search_grammar.parse(tags.strip())
		except lark.exceptions.UnexpectedInput:
			return []
		uses_status_metatag = any(parsed.find_data('status_meta'))
		tx = WorkTagTransformer()
		if tags_parse := tx.transform(parsed):
			q = q & tags_parse
		tag_orderings = tx.orderings
	elif query:
		q = q | Q(worksource__source_id=query)
		if query.startswith('https'):
			q = q | Q(worksource__url=query)
		if search_id > 0:
			q = q | Q(id=search_id)

	if uses_status_metatag:
		qs = MediaWork.active_objects.filter(q)
	else:
		qs = MediaWork.active_objects.filter(q).visible()

	if tag_orderings:
		ann, filter_q, order_fields = tag_orderings[-1]
		if ann:
			qs = qs.annotate(**ann)
		qs = qs.filter(filter_q).order_by(*order_fields)
	elif query:
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
		).order_by('priority', '-id')
	else:
		qs = qs.order_by('-id')

	return qs.distinct()


@work_router.get('tags_needed', response=List[ThinWorkSchema], exclude_none=True)
@paginate
def tags_needed(request: AuthedHttpRequest):
	def has_category(category):
		return Exists(
			TagWorkInstance.objects.filter(
				work=OuterRef('pk'),
				work_tag__deprecated=False,
				work_tag__category=category,
			)
		)

	has_source = Exists(
		TagWorkInstance.objects.filter(
			work=OuterRef('pk'),
			work_tag__deprecated=False,
		).filter(
			Q(work_tag__category=WorkTagCategory.SOURCE)
			| Q(
				work_tag__category__in=[
					WorkTagCategory.CREATOR,
					WorkTagCategory.MEDIA,
					WorkTagCategory.SONG,
				],
				used_as_source=True,
			)
		)
	)

	def missing(flag):
		return Case(
			When(**{flag: False}, then=Value(1)),
			default=Value(0),
			output_field=IntegerField(),
		)

	return (
		MediaWork.active_objects.visible()
		.annotate(
			has_creator=has_category(WorkTagCategory.CREATOR),
			has_song=has_category(WorkTagCategory.SONG),
			has_general=has_category(WorkTagCategory.GENERAL),
			has_source=has_source,
			ntags=Count('tags', filter=Q(tags__deprecated=False)),
		)
		.annotate(
			missing_count=missing('has_creator')
			+ missing('has_song')
			+ missing('has_general')
			+ missing('has_source'),
		)
		.order_by('-missing_count', 'ntags', 'id')
	)


@work_router.get('work', response=WorkSchema)
def work(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.objects.with_pending_moderation(), id=work_id)
	if work.moved_to:
		work = work.moved_to

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
