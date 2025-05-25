from typing import List
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import video_info, playlist_info
from otodb.models import Pool, PoolItem, WorkSource, TagWork, TagWorkInstance, MediaWork
from otodb.account.models import Account

from .common import ListSchema, ListItemSchema

list_router = Router()

@list_router.get('search', response=List[ListSchema])
@paginate
def search(request: HttpRequest, query: str):
    return Pool.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

@list_router.get('list', response=ListSchema)
def lst(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    return list_

@list_router.get('entries', response=List[ListItemSchema])
@paginate
def entries(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    return list_.poolitem_set.order_by('order')

class ListItemInSchema(ModelSchema):
    work_id: int
    class Meta:
        model = PoolItem
        fields = ['description']

class ListInSchema(ModelSchema):
    class Meta:
        model = Pool
        fields = ['name', 'description']

@list_router.post('list', auth=django_auth, response=int)
def new(request: HttpRequest, payload: ListInSchema):
    lst = Pool.objects.create(author=request.user, **payload.dict())
    return lst.id

@list_router.put('list', auth=django_auth)
def update(request: HttpRequest, list_id: int, payload: ListInSchema):
    lst = get_object_or_404(Pool, id=list_id)
    if lst.author != request.user:
        return 403

    lst.name = payload.name
    lst.description = payload.description
    lst.save()

class ListUpdateSchema(Schema):
    # Diffs applied in this exact order: WorkIDs -> Descriptions -> Moves -> Delete
    update_work: List[tuple[int, int]] = []
    update_description: List[tuple[int, str]] = []
    move: List[tuple[int, int]] = [] # [(from, to)]
    delete: List[int] = [] # delete at index

@list_router.put('items', auth=django_auth)
def update_items(request: HttpRequest, list_id: int, payload: ListUpdateSchema):
    lst = get_object_or_404(Pool, id=list_id)

    items = lst.poolitem_set
    
    for (i, new_work) in payload.update_work:
        items.filter(order=i).update(work_id=new_work)
    
    for (i, new_desc) in payload.update_description:
        items.filter(order=i).update(description=new_desc)

    for (a, b) in payload.move:
        items.get(order=a).to(b)

    items.filter(order__in=payload.delete).delete()

    return

@list_router.get('work_in_pool', response=bool)
def work_in_pool(request: HttpRequest, list_id: int, work_id: int):
    lst = get_object_or_404(Pool, pk=list_id)
    return lst.work_in_pool(work_id)

@list_router.put('toggle_work', auth=django_auth)
def toggle(request: HttpRequest, list_id: int, work_id: int):
    lst = get_object_or_404(Pool, pk=list_id)
    if lst.author != request.user:
        return 403

    if entries := lst.work_in_pool(work_id):
        for entry in entries:
            entry.delete()
        return False
    else:
        lst.add_work(work_id)
        return True

@list_router.delete('list', auth=django_auth)
def delete(request: HttpRequest, list_id: int):
    lst = get_object_or_404(Pool, id=list_id)
    if lst.author != request.user:
        return 403
    lst.delete()
    return

@list_router.post('import', auth=django_auth, response=int)
def import_ext(request: HttpRequest, url: str):
    info = playlist_info(url)
    list_ = Pool.objects.create(name=info['title'], description=info['description'], author=request.user)

    with ProcessPoolExecutor(mp_context=multiprocessing.get_context("fork")) as executor:
        infos = executor.map(video_info, info['entries'])

    new_tag_instances, pool_items = [], []
    for i, vid_info in enumerate(list(infos)):
        if vid_info is None:
            list_.description += f'\nFailed to fetch {info['entries'][i]}'
            continue

        src, _ = WorkSource.from_url(vid_info['url'], user=request.user, is_reupload=False, info=vid_info)
        if src.rejection_reason is not None:
            continue
        elif src.media is not None or request.user.level >= Account.Levels.MODERATOR:
            if src.media is not None:
                work = src.media
            else:
                work = MediaWork.objects.create(title=src.title, description=src.description, thumbnail=src.thumbnail)
                src.media = work
                src.save()
            new_tag_instances.extend([TagWorkInstance(work=work, work_tag=TagWork.objects.get_or_create(name=t)[0]) for t in vid_info['tags']])
            pool_items.append(PoolItem(work=work, description='', pool=list_))
        elif src.media is None:
            list_.pending_items.add(src)

    TagWorkInstance.objects.bulk_create(new_tag_instances, ignore_conflicts=True) # bulk_create does not handle M2M so we do this manually
    PoolItem.objects.bulk_create(pool_items)
    return list_.id
