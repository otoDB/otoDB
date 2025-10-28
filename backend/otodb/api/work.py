from typing import List, Literal

from django.http import HttpRequest
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
	clean_incoming_slug,
	process_video_info,
)
from otodb.models import (
	MediaWork,
	WorkRelation,
	WorkSource,
	TagWorkInstance,
	WorkSourceRejection,
	TagWork,
	UserRequest,
	TagWorkCreatorConnection,
)
from otodb.models.enums import (
	Platform,
	WorkOrigin,
	Rating,
	WorkTagCategory,
	RequestActions,
	Status,
	ProfileConnectionTypes,
)
from otodb.account.models import Account

from .common import (
	WorkSchema,
	ThinWorkSchema,
	WorkSourceSchema,
	Error,
	TagWorkSchema,
	user_is_trusted,
	user_is_editor,
	RelationSchema,
	post_relation,
	SlimWorkSchema,
	RouterWithRevision
)

work_router = RouterWithRevision()


class ExternalQuery(Schema):
	work_id: int
	tags: List[TagWorkSchema]


@work_router.get('query_external', response=ExternalQuery)
def query_external(
	request: HttpRequest,
	url: str | None = None,
	platform: str | None = None,
	id: str | None = None,
):
	if url:
		work = get_object_or_404(WorkSource.active_objects, url=url)
	elif platform and id:
		work = get_object_or_404(
			WorkSource.active_objects,
			platform=Platform.from_str(platform),
			source_id=id,
		)
	else:
		# TODO: raise a more specific error
		raise ValueError(
			"Either 'url' or both 'platform' and 'id' parameters must be provided"
		)

	return {'tags': work.media.tags, 'work_id': work.media.id}


@work_router.get('search', response=List[ThinWorkSchema], exclude_none=True)
@paginate
def search(
	request: HttpRequest,
	query: str,
	tags: str | None = None,
	order: Literal['id', '-id', 'pub', '-pub'] | None = '-id',
):
	search_id = int(query) if query.isdigit() else -1
	q = Q(title__icontains=query) | Q(description__icontains=query)
	if tags:
		for tag in tags.split():
			try:
				match tag[0]:
					case '-' | '+' | '!':
						t = TagWork.objects.get(slug=clean_incoming_slug(tag[1:]))
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
						t = TagWork.objects.get(slug=clean_incoming_slug(tag))
						if t.aliased_to:
							t = t.aliased_to

						q = q & Q(tags=t)
			except TagWork.DoesNotExist:
				return []
	else:
		q = q | Q(worksource__source_id=query)
		if query.startswith('https'):
			q = q | Q(worksource__url=query)
		if search_id > 0:
			q = q | Q(id=search_id)

	return (
		MediaWork.objects.filter(moved_to__isnull=True).filter(q)
		.annotate(
			priority=Case(
				When(id=search_id, then=Value(0)),
				When(worksource__url=query, then=Value(1)),
				When(worksource__source_id=query, then=Value(2)),
				When(
					Q(title__icontains=query) | Q(description__icontains=query),
					then=Value(100),
				),
				default=Value(1000),
				output_field=IntegerField(),
			),
			pub=Subquery(
				WorkSource.objects.filter(media_id=OuterRef('id'))
				.order_by('published_date')
				.values('published_date')[:1]
			),
		)
		.order_by('priority', order)
		.distinct()
	)


@work_router.get('tags_needed', response=List[ThinWorkSchema], exclude_none=True)
@paginate
def tags_needed(request: HttpRequest):
	return (
		MediaWork.objects.filter(moved_to__isnull=True).annotate(
			ntags=Count('tags', filter=Q(tags__deprecated=False))
		)
		.filter(ntags__lte=4)
		.order_by('ntags')
		.distinct()
	)


@work_router.get('work', response={200: WorkSchema, 300: int})
def work(request: HttpRequest, work_id: int):
	work = get_object_or_404(
		MediaWork.objects.select_related('thumbnail_source'), id=work_id
	)
	if work.moved_to:
		return 300, work.moved_to.id
	return work


@work_router.delete('work', auth=django_auth)
@user_is_editor
def delete_work(request: HttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	work.worksource_set.update(media=None)
	work.delete()


@work_router.put('set_tags', auth=django_auth)
@user_is_trusted
def set_tags(request: HttpRequest, work_id: int, payload: List[str]):
	work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)

	tags = []
	for v in payload:
		try:
			tags.append(TagWork.objects.get(slug=clean_incoming_slug(v)))
		except TagWork.DoesNotExist:
			tags.append(TagWork.objects.create(name=v))

	work.tags.remove(*work.tags.exclude(id__in=[t.id for t in tags]))
	work.tags.add(*tags)

	return 200


class CreatorRolesUpdateSchema(Schema):
	work_id: int
	tag_slug: str
	creator_roles: List[int]


@work_router.post('creator_roles', auth=django_auth)
@user_is_trusted
def update_creator_roles(request: HttpRequest, payload: CreatorRolesUpdateSchema):
	instance = get_object_or_404(
		TagWorkInstance, work_id=payload.work_id, work_tag__slug=payload.tag_slug
	)

	if instance.work_tag.category == WorkTagCategory.CREATOR:
		instance.set_creator_roles(payload.creator_roles)
		instance.save()

	return 200


@work_router.put('toggle_sample', auth=django_auth)
@user_is_trusted
def toggle_sample(request: HttpRequest, work_id: int, tag_slug: str):
	instance = get_object_or_404(
		TagWorkInstance, work_id=work_id, work_tag__slug=tag_slug
	)
	instance.used_as_source = not instance.used_as_source
	instance.save()


@work_router.put('remove_tag', auth=django_auth)
@user_is_trusted
def remove_tag(request: HttpRequest, work_id: int, tag_slug: str):
	work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	tag = get_object_or_404(TagWork, slug=tag_slug)
	work.tags.remove(tag)
	if tag.can_be_deleted:
		tag.delete()


@work_router.get('random', response=list[ThinWorkSchema], exclude_none=True)
def random(request: HttpRequest, n: int = 1):
	return (
		MediaWork.objects.filter(moved_to__isnull=True).select_related('thumbnail_source')
		.prefetch_related('tags', 'tags__aliases', 'tags__tagworklangpreference_set')
		.filter(rating=Rating.GENERAL)
		.order_by('?')[: min(n, 20)]
	)


@work_router.get('recent', response=list[ThinWorkSchema], exclude_none=True)
def recent(request: HttpRequest, n: int = 1):
	return (
		MediaWork.objects.filter(moved_to__isnull=True).select_related('thumbnail_source')
		.prefetch_related('tags', 'tags__aliases', 'tags__tagworklangpreference_set')
		.order_by('-id')[: min(n, 20)]
	)


@work_router.get(
	'relations', response=tuple[list[RelationSchema], list[SlimWorkSchema]]
)
def relations(request: HttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	relations = WorkRelation.get_component(work.id)
	return 200, (relations, {w.id: w for r in relations for w in (r.A, r.B)}.values())


@work_router.post('relation', auth=django_auth)
@user_is_trusted
def relation(request: HttpRequest, payload: RelationSchema):
	post_relation(MediaWork, payload)
	return


@work_router.delete('relation', auth=django_auth)
@user_is_trusted
def delete_relation(request: HttpRequest, A: int, B: int):
	a = MediaWork.objects.filter(moved_to__isnull=True).get(id=A)
	b = MediaWork.objects.filter(moved_to__isnull=True).get(id=B)
	rel = WorkRelation.objects.get(a, b)
	rel.delete()
	return


@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: HttpRequest, work_id: int):
	work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	return work.worksource_set


@work_router.post('unbind_source', auth=django_auth)
@user_is_editor
def unbind_sources(request: HttpRequest, source_id: int):
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	if src.media.worksource_set.count() == 1:
		src.media.delete()
	src.media = None
	src.save()


@work_router.put('source_origin', auth=django_auth)
@user_is_editor
def source_origin(request: HttpRequest, source_id: int, status: int):
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	src.work_origin = WorkOrigin(status).value
	src.save()


@work_router.post('refresh_source', auth=django_auth)
def refresh_source(request: HttpRequest, source_id: int):
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	src.refresh()
	return


class WorkEditSchema(ModelSchema):
	class Meta:
		model = MediaWork
		fields = ['title', 'description', 'thumbnail_source', 'rating']


@work_router.post('merge', auth=django_auth)
@user_is_editor
def merge_works(
	request: HttpRequest, from_work_id: int, to_work_id: int, payload: WorkEditSchema
):
	MediaWork.merge(
		to_work=get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=to_work_id),
		from_work=get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=from_work_id),
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
def update_work(
	request: HttpRequest, work_id: int, payload: WorkEditSchema, reason: str
):
	work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	for attr, value in payload.dict().items():
		if attr == 'thumbnail_source' and value is not None:
			value = get_object_or_404(WorkSource.active_objects, id=value)
		setattr(work, attr, value)
	work.save()
	return


@work_router.post(
	'source', auth=django_auth, response={200: int | None, 400: Error, 409: Error}
)
@user_is_trusted
def new_source_from_url(
	request: HttpRequest,
	url: str,
	is_reupload: bool,
	rating: int = 0,
	work_id: int | None = None,
	original_url: str | None = None,
):
	"""Creates a new source and, for editors, performs auto-validation as well as Work creation

	The priority for redirections/merging is:.

	The usage scenarios are as follows:
	- For non-editors:
	    - Adding a new source leaves it in the approval queue, without creating a Work;
	    - If `work_id` is provided, or either of the original/reupload Source already has a Work, the new sources are added to them;
	        - If two out of three elements have works, the third element is added based on priority: `work_id` > `url` > `original_url`;
	    - Adding an existing source redirects to the corresponding work;
	    - Adding multiple sources, each with a different work, redirects based on priority: `work_id` > `url` > `original_url`;
	    - For existing sources/works, corrections (`rating`/`is_reupload`) are ignored;
	- For editors:
	    - Adding a new source creates a new Work;
	    - For existing sources/works, corrections (`rating`/`is_reupload`) are applied;
	    - If any or all of `work_id`/`url`/`original_url` have different Works, a merge is performed based on priority: `work_id` > `url` > `original_url.
	"""

	is_editor = request.user.level >= Account.Levels.EDITOR

	# === Source retrieval, common to all flows ===

	src, info = WorkSource.from_url(url, user=request.user, is_reupload=is_reupload)

	original_src, original_info = (
		WorkSource.from_url(original_url, user=request.user, is_reupload=False)
		if original_url
		else (None, None)
	)

	if src is None or original_url and original_src is None:
		return 400, {'message': 'Bad request, is the URL correct?'}

	if getattr(src, 'rejection', None) or getattr(original_src, 'rejection', None):
		return 400, {'message': 'Bad Request, This source has already been rejected'}

	# === Work check: no work, and not editor ===
	original_src_media = original_src.media if original_src else None
	none_have_work = not work_id and not src.media and not original_src_media
	if none_have_work and not is_editor:
		return

	# === Work check: both have  Works ===

	all_have_work = src.media and original_src_media
	if all_have_work and (src.media.id == original_src.media.id or not is_editor):
		return src.media.id

	# === Work check: editor flow or existing work found in request/sources ===

	if work_id:
		work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	elif src.media:
		work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=src.media.id)
	elif original_src and original_src_media is not None:
		work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=original_src.media.id)
	else:
		work = MediaWork.objects.create(
			title=src.title,
			description=src.description,
			thumbnail_source=src,
			rating=rating,
		)

	sync_work_source(work, src, info, is_editor)
	if original_src:
		sync_work_source(work, original_src, original_info, is_editor)

	# update_fields is necessary here because previous merges will change
	# the "media" field in a way that's not tracked by the current
	# object.
	if is_editor:
		if work.rating != rating:
			work.rating = rating
			work.save(update_fields=['rating'])
		if src.work_origin != WorkOrigin(is_reupload):
			src.work_origin = WorkOrigin(is_reupload)
			src.save(update_fields=['work_origin'])
		if original_src and original_src.work_origin != WorkOrigin.AUTHOR:
			original_src.work_origin = WorkOrigin.AUTHOR
			original_src.save(update_fields=['work_origin'])

	return work.id


def sync_work_source(work: MediaWork, src: WorkSource, info, can_merge):
	"""Syncs source data to its work

	- Syncs tags and assigns the source to a work if orphan source;
	- Merges the work if `can_merge` is passed and the source has an existing, different work id.
	- Does nothing if the source is already assigned to the work;
	"""

	if not src.media:
		work.tags.add(
			*info.get('tags', []),
			*TagWork.objects.filter(
				id__in=UserRequest.objects.filter(
					command=RequestActions.WORKSOURCE_ATTACHTAG,
					A_id=src.id,
					bulk__status=Status.APPROVED,
				).values('B_id')
			),
			*(
				TagWork.objects.filter(
					id__in=(
						TagWorkCreatorConnection.objects.filter(
							site=ProfileConnectionTypes.YOUTUBE
						).filter(
							Q(content_id=info['uploader_id'])
							| Q(content_id='channel/' + info['channel_id'])
						)
						if src.platform == Platform.YOUTUBE
						else TagWorkCreatorConnection.objects.filter(
							site=ProfileConnectionTypes[Platform(src.platform).name],
							content_id=info['uploader_id'],
						)
					).values('tag_id')
				)
				if src.work_origin == WorkOrigin.AUTHOR
				else []
			),
		)
		tags = TagWork.objects.filter(name__in=info.get('tags', []))
		work.tagworkinstance_set.filter(work_tag__in=tags).update(
			instance_imported_from_source=True
		)
		src.media = work
		src.save()
	elif can_merge and src.media.id != work.id:
		MediaWork.merge(
			from_work=src.media,
			to_work=work,
			title=work.title,
			description=work.description,
			thumbnail_source=src,
			rating=work.rating,
		)


@work_router.post(
	'assign_source',
	auth=django_auth,
	description='Omit work_id if creating new work from source.',
	response=int,
)
@user_is_editor
def assign_source_to_work(
	request: HttpRequest, source_id: int, work_id: int | None = None
):
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	assert src.media is None and not getattr(src, 'rejection', None)

	if work_id is not None:
		work = get_object_or_404(MediaWork.objects.filter(moved_to__isnull=True), id=work_id)
	else:
		work = MediaWork.objects.create(
			title=src.title, description=src.description, thumbnail_source=src
		)

	# Add them first in case they don't exist
	info = process_video_info(src.info_payload.payload, src.url)
	sync_work_source(work, src, info, False)

	for pool in src.pool_set.all():
		pool.add_work(work.id)
		pool.pending_items.remove(src)

	return work.id


@work_router.post('reject_source', auth=django_auth)
@user_is_editor
def reject_source(request: HttpRequest, source_id: int, reason: str):
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	src.rejection = WorkSourceRejection.objects.create(
		source=src, by=request.user, reason=reason
	)
	src.save()
	return


@work_router.get('unbound', auth=django_auth, response=List[WorkSourceSchema])
@user_is_editor
def get_unbound_sources(request: HttpRequest, pending: bool):
	return WorkSource.objects.filter(media__isnull=True, rejection__isnull=pending)
