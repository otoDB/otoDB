import asyncio

from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import aget_object_or_404, get_object_or_404
from ninja import ModelSchema, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.common import playlist_info, video_info
from otodb.models import (
	Pool,
	PoolItem,
	PoolUpstream,
	WorkSource,
)

from .common import (
	ListItemSchema,
	ListSchema,
	OtodbID,
	WorkSourceSchema,
	track_revision,
	user_is_editor,
)

list_router = Router()


@list_router.get('search', response=list[ListSchema])
@paginate
def search(request: HttpRequest, query: str):
	return Pool.objects.filter(
		Q(name__icontains=query) | Q(description__icontains=query)
	)


@list_router.get('list', response=ListSchema)
def lst(request: HttpRequest, list_id: OtodbID):
	list_ = get_object_or_404(Pool, pk=list_id)
	return list_


@list_router.get('entries', response=list[ListItemSchema])
@paginate
def entries(request: HttpRequest, list_id: OtodbID):
	list_ = get_object_or_404(Pool, pk=list_id)
	return list_.poolitem_set.order_by('order')


@list_router.get('pending', response=list[WorkSourceSchema])
@paginate
def pending(request: HttpRequest, list_id: OtodbID):
	list_ = get_object_or_404(Pool, pk=list_id)
	return list_.pending_items.all()


class ListItemInSchema(ModelSchema):
	work_id: OtodbID

	class Meta:
		model = PoolItem
		fields = ['description']


class ListInSchema(ModelSchema):
	class Meta:
		model = Pool
		fields = ['name', 'description']


@list_router.post('list', auth=django_auth, response=OtodbID)
def new(request: HttpRequest, payload: ListInSchema):
	lst = Pool.objects.create(author=request.user, **payload.dict())
	return lst.id


@list_router.put('list', auth=django_auth)
def update(request: HttpRequest, list_id: OtodbID, payload: ListInSchema):
	lst = get_object_or_404(Pool, id=list_id)
	if lst.author != request.user:
		raise HttpError(403, 'Forbidden')

	lst.name = payload.name
	lst.description = payload.description
	lst.save()


class ListUpdateSchema(Schema):
	# Diffs applied in this exact order: WorkIDs -> Descriptions -> Moves -> Delete
	update_work: list[tuple[int, OtodbID]] = []
	update_description: list[tuple[int, str]] = []
	move: list[tuple[int, int]] = []  # [(from, to)]
	delete: list[int] = []  # delete at index


@list_router.put('items', auth=django_auth)
def update_items(request: HttpRequest, list_id: OtodbID, payload: ListUpdateSchema):
	lst = get_object_or_404(Pool, id=list_id)

	items = lst.poolitem_set

	for i, new_work in payload.update_work:
		items.filter(order=i).update(work_id=new_work)

	for i, new_desc in payload.update_description:
		items.filter(order=i).update(description=new_desc)

	for a, b in payload.move:
		items.get(order=a).to(b)

	items.filter(order__in=payload.delete).delete()


@list_router.get('work_in_pool', response=bool)
def work_in_pool(request: HttpRequest, list_id: OtodbID, work_id: OtodbID):
	lst = get_object_or_404(Pool, pk=list_id)
	return lst.work_in_pool(work_id)


@list_router.put('toggle_work', auth=django_auth)
def toggle(request: HttpRequest, list_id: OtodbID, work_id: OtodbID):
	lst = get_object_or_404(Pool, pk=list_id)
	if lst.author != request.user:
		raise HttpError(403, 'Forbidden')

	if entries := lst.work_in_pool(work_id):
		entries.delete()
		return False
	else:
		lst.add_work(work_id)
		return True


@list_router.delete('list', auth=django_auth)
def delete(request: HttpRequest, list_id: OtodbID):
	lst = get_object_or_404(Pool, id=list_id)
	if lst.author != request.user:
		raise HttpError(403, 'Forbidden')
	lst.delete()


def import_ext_into_pool(entries, infos, list_: Pool, user):
	# set() instead of .distinct() because list has not yet been written to the DB
	existing_work_ids = set(list_.poolitem_set.values_list('work__id', flat=True))

	new_works = {}
	for entry, (vid_info, full_info) in zip(entries, infos):
		if vid_info is None:
			list_.description += f'\nFailed to fetch {entry}'
			continue

		src = WorkSource.from_url(
			vid_info['url'],
			info=vid_info,
			full_info=full_info,
			user=user,
			is_reupload=False,
		)

		if src is None:
			list_.description += f'\nFailed to fetch {entry}'
			continue

		if src.media is None:
			# No work yet - add to pending for user review
			list_.pending_items.add(src)
		elif src.media.pk not in existing_work_ids:
			# Source already has a work - add to pool if not already there
			new_works[src.media.pk] = src.media

	list_.save()
	PoolItem.objects.bulk_create(
		[PoolItem(work=work, description='', pool=list_) for work in new_works.values()]
	)


@list_router.post(
	'import', auth=django_auth, response=OtodbID, throttle=[AuthRateThrottle('3/30m')]
)
@user_is_editor
@track_revision
async def import_ext(request: HttpRequest, url: str):
	info = await playlist_info(url)
	infos = await asyncio.gather(*[video_info(v) for v in info['entries']])

	@transaction.atomic
	def make_pool():
		list_ = Pool.objects.create(
			name=info['title'], description=info['description'], author=request.user
		)
		PoolUpstream.objects.create(pool=list_, upstream=url)
		import_ext_into_pool(info['entries'], infos, list_, request.user)
		return list_.id

	list_id = await sync_to_async(make_pool)()

	return list_id


@list_router.post('pull_upstream', auth=django_auth)
async def pull_upstream(request: HttpRequest, list_id: OtodbID):
	lst = await aget_object_or_404(
		Pool.objects.select_related('poolupstream'), id=list_id
	)
	if lst.author_id != request.user.id:
		raise HttpError(403, 'Forbidden')

	info = await playlist_info(lst.poolupstream.upstream)

	infos = await asyncio.gather(*[video_info(v) for v in info['entries']])
	await sync_to_async(transaction.atomic(import_ext_into_pool))(
		info['entries'], infos, lst, request.user
	)
