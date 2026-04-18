from typing import Annotated
from datetime import date
from pydantic import StringConstraints

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ninja import Schema
from ninja.security import django_auth

from otodb.common import process_video_info, slugify_tag
from otodb.models import (
	MediaWork,
	WorkSource,
	TagWork,
	TagWorkCreatorConnection,
)
from otodb.models.enums import (
	ErrorCode,
	Platform,
	WorkOrigin,
	ProfileConnectionTypes,
	Route,
	WorkStatus,
)
from otodb.account.models import Account

from .common import (
	AuthedHttpRequest,
	TagWorkSchema,
	WorkSourceSchema,
	SourceCreationResponse,
	SourceSuggestionsResponse,
	Error,
	user_is_trusted,
	user_is_editor,
	RouterWithRevision,
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
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	if src.media.worksource_set.count() == 1:
		src.media.delete()
	src.media = None
	src.save()


@source_router.put('origin', auth=django_auth)
@user_is_editor
@with_revision_route(Route.WORKSOURCE_SET_ORIGIN)
def source_origin(request: AuthedHttpRequest, source_id: int, status: WorkOrigin):
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	src.work_origin = status.value
	src.save()


@source_router.post('refresh', auth=django_auth)
@user_is_editor
@with_revision_route(Route.WORKSOURCE_REFRESH)
def refresh_source(request: AuthedHttpRequest, source_id: int):
	src: WorkSource = get_object_or_404(WorkSource.active_objects, id=source_id)
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
		WorkSource.active_objects, id=source_id, work_status=WorkStatus.DOWN
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
		return 403, {
			'code': ErrorCode.EDITOR_ONLY,
			'data': {'message': 'Only editors can make changes here.'},
		}

	metadata_dict = metadata.dict() if metadata else None
	src, info = WorkSource.from_url(
		url, user=request.user, is_reupload=is_reupload, metadata=metadata_dict
	)

	if src is None:
		return 400, {
			'code': ErrorCode.BAD_URL,
			'data': {'message': 'Bad request, is the URL correct?'},
		}

	# Source already has a work -> redirect
	if src.media:
		return {'work_id': src.media.pk}

	# work_id provided -> bind source to existing work
	if work_id:
		work = get_object_or_404(
			MediaWork.objects.filter(moved_to__isnull=True), id=work_id
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


@source_router.get('suggestions', auth=django_auth, response=SourceSuggestionsResponse)
@user_is_trusted
def source_suggestions(request: AuthedHttpRequest, source_id: int):
	"""Returns tag suggestions derived from a source's info_payload."""
	src = get_object_or_404(WorkSource.active_objects, id=source_id)
	if not hasattr(src, 'info_payload'):
		return {'title': src.title, 'description': src.description}

	info = process_video_info(src.info_payload.payload, src.url)
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

	return {
		'title': src.title,
		'description': src.description,
		'source_tags': existing,
		'new_tags': new_tags,
		'creator_tags': creator_tags,
	}
