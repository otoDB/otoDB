from datetime import date
from typing import Annotated

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Schema
from ninja.pagination import paginate
from ninja.security import django_auth
from pydantic import StringConstraints

from otodb.account.models import Account
from otodb.common import process_video_info, slugify_tag
from otodb.models import (
	MediaWork,
	ModerationEvent,
	TagWork,
	TagWorkCreatorConnection,
	WorkSource,
)
from otodb.models.enums import (
	ErrorCode,
	FlagStatus,
	ModerationAction,
	ModerationEventType,
	Platform,
	ProfileConnectionTypes,
	Route,
	Status,
	WorkOrigin,
	WorkStatus,
)
from otodb.tasks import enqueue_deferred, resolve_expired_source_task

from .common import (
	ApiError,
	AuthedHttpRequest,
	Error,
	RouterWithRevision,
	SourceCreationResponse,
	SourceSuggestionsResponse,
	TagWorkSchema,
	WorkSourceSchema,
	ensure_can_moderate,
	user_is_editor,
	user_is_trusted,
	with_revision_route,
)

source_router = RouterWithRevision()


class WorkSourceMetadataSchema(Schema):
	"""Manual WorkSource metadata input"""

	title: str | None = None
	description: str | None = None
	uploader_id: str | None = None
	thumbnail_url: str | None = None
	work_width: int | None = None
	work_height: int | None = None
	work_duration: int | None = None
	published_date: date | None = None


@source_router.post('unbind', auth=django_auth)
@user_is_editor
@with_revision_route(Route.WORKSOURCE_UNBIND)
def unbind_source(request: AuthedHttpRequest, source_id: int):
	src = get_object_or_404(WorkSource.objects, id=source_id)
	if src.media.worksource_set.count() == 1:
		src.media.delete()
	src.media = None
	src.save()


@source_router.put('origin', auth=django_auth)
@user_is_editor
@with_revision_route(Route.WORKSOURCE_SET_ORIGIN)
def source_origin(request: AuthedHttpRequest, source_id: int, status: WorkOrigin):
	src = get_object_or_404(WorkSource.objects, id=source_id)
	src.work_origin = status
	src.save()


@source_router.post('refresh', auth=django_auth)
@user_is_editor
@with_revision_route(Route.WORKSOURCE_REFRESH)
def refresh_source(request: AuthedHttpRequest, source_id: int):
	src: WorkSource = get_object_or_404(WorkSource.objects, id=source_id)
	src.refresh()
	return


@source_router.get('source', response=WorkSourceSchema)
def get_source(request, source_id: int):
	return get_object_or_404(WorkSource, id=source_id)


@source_router.put('source', auth=django_auth, response={200: int, 400: Error})
@user_is_editor
@with_revision_route(Route.WORKSOURCE_UPDATE)
def update_source(
	request: AuthedHttpRequest, source_id: int, metadata: WorkSourceMetadataSchema
):
	src = get_object_or_404(
		WorkSource.objects, id=source_id, work_status=WorkStatus.DOWN
	)
	src.title = metadata.title
	src.description = metadata.description
	src.uploader_id = metadata.uploader_id

	src.thumbnail_url = metadata.thumbnail_url

	src.work_width = metadata.work_width
	src.work_height = metadata.work_height
	src.work_duration = metadata.work_duration
	src.published_date = metadata.published_date

	src.save_thumbnail()
	src.save()

	return src.media.pk


@source_router.post(
	'source',
	auth=django_auth,
	response={200: SourceCreationResponse, 400: Error},
)
@user_is_trusted
@transaction.atomic
@with_revision_route(Route.WORKSOURCE_CREATE)
def new_source_from_url(
	request: AuthedHttpRequest,
	url: Annotated[str, StringConstraints(strip_whitespace=True)],
	is_reupload: bool,
	work_id: int | None = None,
	metadata: WorkSourceMetadataSchema | None = None,
):
	"""Creates or retrieves a source from a URL.

	- If the source already has a work, returns work_id (redirect to work page).
	- If work_id is provided, binds the source to that work.
	- Otherwise, returns source_id for the user to review and create a work.
	"""
	is_editor = request.user.level >= Account.Levels.EDITOR

	if metadata is not None and not is_editor:
		raise ApiError(403, ErrorCode.EDITOR_ONLY)

	metadata_dict = metadata.dict() if metadata else None
	src, info = WorkSource.from_url(
		url, user=request.user, is_reupload=is_reupload, metadata=metadata_dict
	)

	if src is None:
		raise ApiError(400, ErrorCode.BAD_URL)

	# Source already has a work -> redirect
	if src.media:
		return {'work_id': src.media.pk}

	# work_id provided -> bind source to existing work
	if work_id:
		work = get_object_or_404(
			MediaWork.objects.filter(moved_to__isnull=True), id=work_id
		)
		if work.status == Status.UNAPPROVED:
			raise ApiError(400, ErrorCode.SOURCE_UNAPPROVED)
		if work.moderation_events.filter(
			event_type=ModerationEventType.FLAG, status=FlagStatus.PENDING
		).exists():
			raise ApiError(400, ErrorCode.SOURCE_FLAGGED)
		if not is_editor and work.status == Status.APPROVED:
			src.is_pending = True
			transaction.on_commit(
				lambda: enqueue_deferred(
					resolve_expired_source_task,
					src.pk,
					delay=settings.OTODB_MODERATION_PERIOD,
				)
			)
		sync_work_source(work, src)
		return {'work_id': work.pk}

	# New source, no existing work -> return source_id for review
	return {'source_id': src.pk}


def resolve_creator_tags(src: WorkSource, info: dict) -> list:
	"""Resolve creator tags from source uploader info."""
	creator_tags = []
	platform_name = Platform(src.platform).name
	if (
		src.work_origin == WorkOrigin.AUTHOR
		and info.get('uploader_id')
		and platform_name in ProfileConnectionTypes.__members__
	):
		q = TagWorkCreatorConnection.objects.filter(
			site=ProfileConnectionTypes[platform_name]
		)

		if src.platform == Platform.YOUTUBE and info.get('channel_id'):
			q = q.filter(
				Q(content_id=info['uploader_id'])
				| Q(content_id='channel/' + info['channel_id'])
			)
		elif src.platform == Platform.TWITTER:
			q = q.filter(
				Q(content_id=info['uploader_id'])
				| Q(content_id__endswith='/' + info['channel_id'])
				| Q(content_id__endswith='user_id=' + info['channel_id'])
			)
		elif src.platform == Platform.SOUNDCLOUD:
			q = q.filter(content_id=info['url'].split('/')[3])
		else:
			q = q.filter(content_id=info['uploader_id'])

		creator_tags = list(TagWork.objects.filter(id__in=q.values('tag_id')))
	return creator_tags


def sync_work_source(work: MediaWork, src: WorkSource):
	"""Binds an unbound source to a work, or merges if the source has a different work."""
	if not src.media:
		src.media = work
		src.save()
	elif src.media.pk != work.pk:
		MediaWork.merge(
			from_work=src.media,
			to_work=work,
			title=work.title,
			description=work.description,
			thumbnail_source=src,
			rating=work.rating,
		)


def extract_source_tag_suggestions(src: WorkSource):
	if not hasattr(src, 'info_payload'):
		return [], [], []

	info = process_video_info(src.info_payload.payload, src.url)
	if info is None:
		return [], [], []
	raw_tags = info.get('tags', [])
	slug_to_name: dict[str, str] = {slugify_tag(t): t for t in raw_tags}
	matched = TagWork.objects.filter(slug__in=slug_to_name.keys())
	existing_names = {slug_to_name[t.slug] for t in matched}
	resolved = {(t.aliased_to or t).pk: (t.aliased_to or t) for t in matched}
	existing = list(
		TagWork.objects.filter(pk__in=resolved.keys(), deprecated=False)
		if resolved
		else []
	)
	new_tags = [
		TagWorkSchema(
			id=0,
			name=t,
			slug=t,
			category=0,
			lang_prefs=[],
			aliased_to=None,
			deprecated=False,
		)
		# Deduplicate -- see PR #467
		for t in set(raw_tags) - existing_names
	]
	creator_tags = resolve_creator_tags(src, info)
	return existing, new_tags, creator_tags


@source_router.get('suggestions', auth=django_auth, response=SourceSuggestionsResponse)
@user_is_trusted
def source_suggestions(request: AuthedHttpRequest, source_id: int):
	"""Returns tag suggestions derived from a source's info_payload."""
	src = get_object_or_404(WorkSource.objects, id=source_id)
	if not hasattr(src, 'info_payload'):
		return {'title': src.title, 'description': src.description}

	source_tags, new_tags, creator_tags = extract_source_tag_suggestions(src)
	return {
		'title': src.title,
		'description': src.description,
		'source_tags': source_tags,
		'new_tags': new_tags,
		'creator_tags': creator_tags,
	}


def reject_pending_source(src: WorkSource, by, reason: str):
	"""Unbind a pending source from its work and record a MOD_ACTION event."""
	work = src.media  # Capture before unbinding
	src.media = None
	src.is_pending = False
	src.save(update_fields=['media', 'is_pending'])
	ModerationEvent.objects.create(
		work=work,
		source=src,
		event_type=ModerationEventType.MOD_ACTION,
		status=ModerationAction.SOURCE_REJECTED,
		by=by,
		reason=reason,
	)


@source_router.post('reject', auth=django_auth, response={200: None, 403: Error})
@user_is_editor
@with_revision_route(Route.WORKSOURCE_REJECT)
def reject_source(request: AuthedHttpRequest, source_id: int, reason: str):
	"""Reject a pending source on an existing work. Unbinds the source."""
	src = get_object_or_404(WorkSource.objects, id=source_id, is_pending=True)
	ensure_can_moderate(request.user, src.media)
	reject_pending_source(src, by=request.user, reason=reason)


@source_router.post('approve', auth=django_auth, response={200: None, 403: Error})
@user_is_editor
def approve_source(request: AuthedHttpRequest, source_id: int):
	"""Approve a pending source on an existing work."""
	src = get_object_or_404(WorkSource.objects, id=source_id, is_pending=True)
	ensure_can_moderate(request.user, src.media)
	src.is_pending = False
	src.save(update_fields=['is_pending'])
	ModerationEvent.objects.create(
		work=src.media,
		source=src,
		event_type=ModerationEventType.MOD_ACTION,
		status=ModerationAction.SOURCE_APPROVED,
		by=request.user,
	)


@source_router.get('list', response=list[WorkSourceSchema])
@paginate
def list_sources(
	request,
	user_id: int | None = None,
	unbound: bool | None = None,
	is_pending: bool | None = None,
	platform: int | None = None,
):
	"""List sources with pagination, filterable by user, binding, and pending status."""
	qs = WorkSource.objects.select_related('media', 'added_by').order_by('-created_at')
	if user_id:
		qs = qs.filter(added_by_id=user_id)
	if unbound is not None:
		qs = qs.filter(media__isnull=unbound)
	if is_pending is not None:
		qs = qs.filter(is_pending=is_pending)
	if platform is not None:
		qs = qs.filter(platform=platform)
	return qs
