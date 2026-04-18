from typing import List, Literal
from functools import reduce

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import (
	Q,
	Count,
	Value,
	Case,
	When,
	IntegerField,
	Subquery,
	OuterRef,
)

from ninja import Schema, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import (
	slugify_tag,
)
from otodb.models import (
	MediaWork,
	WorkRelation,
	WorkSource,
	TagWorkInstance,
	TagWork,
)
from otodb.models.enums import (
	ErrorCode,
	Platform,
	Rating,
	WorkTagCategory,
	Route,
)

from .common import (
	AuthedHttpRequest,
	WorkSchema,
	ThinWorkSchema,
	WorkSourceSchema,
	CreateWorkPayload,
	TagWorkInstanceInSchema,
	Error,
	TagWorkInstanceSchema,
	user_is_trusted,
	user_is_editor,
	user_is_staff,
	WorkRelationSchema,
	post_relations,
	SlimWorkSchema,
	RouterWithRevision,
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
		work = get_object_or_404(WorkSource.active_objects, url=url)
	elif platform and id:
		work = get_object_or_404(
			WorkSource.active_objects.filter(platform=Platform.from_str(platform)),
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

	qs = MediaWork.active_objects.filter(q).annotate(
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
		MediaWork.active_objects.annotate(
			ntags=Count('tags', filter=Q(tags__deprecated=False))
		)
		.filter(ntags__lte=4)
		.order_by('ntags')
		.distinct()
	)


@work_router.get('work', response=WorkSchema)
def work(request: AuthedHttpRequest, work_id: int):
	return get_object_or_404(MediaWork.objects, id=work_id)


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
	return MediaWork.active_objects.filter(rating=Rating.GENERAL).order_by('?')[
		: min(n, 20)
	]


@work_router.get('recent', response=list[ThinWorkSchema], exclude_none=True)
def recent(request: AuthedHttpRequest, n: int = 1):
	return MediaWork.active_objects.order_by('-id')[: min(n, 20)]


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
			WorkSource.active_objects, id=payload.thumbnail_source
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
			value = get_object_or_404(WorkSource.active_objects, id=value)
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
	src = get_object_or_404(WorkSource.active_objects, id=payload.source_id)
	if src.media is not None:
		return 409, {
			'code': ErrorCode.SOURCE_HAS_WORK,
			'data': {'message': 'Source already has a work'},
		}

	work = MediaWork.objects.create(
		title=payload.title or src.title,
		description=payload.description or src.description,
		thumbnail_source=src,
		rating=payload.rating,
	)

	_resolve_and_apply_tags(work, payload.tags)

	src.media = work
	src.save()

	# Pool assignments
	for pool in src.pool_set.all():
		pool.add_work(work.pk)
		pool.pending_items.remove(src)

	return work.pk


@work_router.get('similar', response=List[ThinWorkSchema])
def similar(request: AuthedHttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.active_objects, id=work_id)
	wt = work.tags.filter(deprecated=False).values_list('id', flat=True)
	return (
		MediaWork.active_objects.exclude(id=work_id)
		.filter(tags__in=Subquery(wt))
		.annotate(shared_tags_count=Count('tags', filter=Q(tags__in=Subquery(wt))))
		.order_by('-shared_tags_count')
	)[:6]
