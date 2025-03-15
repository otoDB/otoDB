from typing import List
from datetime import date
from concurrent.futures import ProcessPoolExecutor

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import video_info, playlist_info
from otodb.models import Pool, PoolItem, WorkSource, MediaWork, TagWork, TagWorkInstance
from otodb.models.enums import WorkOrigin

from .common import ListSchema, ListItemSchema

list_router = Router()

@list_router.get('search', response=List[ListSchema])
@paginate
def search(request: HttpRequest, query: str):
    return Pool.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

@list_router.get('list', response=ListSchema)
def list(request: HttpRequest, list_id: int):
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
        return 401

    lst.name = payload.name
    lst.description = payload.description
    lst.save()

class ListUpdateSchema(Schema):
    # Diffs applied in this exact order: WorkIDs -> Descriptions -> Moves -> Delete -> Insert
    update_work: List[tuple[int, int]] = []
    update_description: List[tuple[int, str]] = []
    move: List[tuple[int, int]] = [] # [(from, to)]
    delete: List[int] = [] # delete at index
    insert_at: List[tuple[int, ListItemInSchema]] = [] # insert before index tuple[0]

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

    for i, item in payload.insert_at:
        item = PoolItem(work_id=item.work_id, description=item.description).create()
        item.to(i)

    return

@list_router.get('work_in_pool', response=bool)
def work_in_pool(request: HttpRequest, list_id: int, work_id: int):
    lst = get_object_or_404(Pool, pk=list_id)
    return lst.work_in_pool(work_id)

@list_router.put('toggle_work', auth=django_auth)
def toggle(request: HttpRequest, list_id: int, work_id: int):
    lst = get_object_or_404(Pool, pk=list_id)
    if lst.author != request.user:
        return 401

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
        return 401
    lst.delete()
    return

# TODO eliminate code that relies on throw behavior of video_info
def video_info_wrapped(url):
    try:
        return video_info(url)
    except:
        return {'failed': url}

@list_router.post('import', auth=django_auth, response=int)
def import_ext(request: HttpRequest, url: str):
    info = playlist_info(url)
    list_ = Pool(name=info['title'], description=info['description'], author=request.user)

    with ProcessPoolExecutor() as executor:
        infos = executor.map(video_info_wrapped, info['entries'])

    new_works, new_tag_instances, new_sources, pool_items = [], [], [], []
    i = 0
    for vid_info in infos:
        if 'failed' in vid_info:
            list_.description += f'\nFailed to fetch {vid_info['failed']}'
            continue

        try:
            src = WorkSource.objects.get(platform=vid_info['site'], source_id=vid_info['id'])
        except WorkSource.DoesNotExist:
            src = None
        if not src:
            work = MediaWork(title=vid_info['title'], description=vid_info['description'], thumbnail=vid_info['thumb'])
            src = WorkSource(media=work, title=vid_info['title'], description=vid_info['description'],
                url=vid_info['url'], platform=vid_info['site'], source_id=vid_info['id'],
                published_date=date.fromtimestamp(vid_info['timestamp']),
                work_origin=WorkOrigin(False), thumbnail=vid_info.get('thumb', None),
                work_width=vid_info.get('work_width',None), work_height=vid_info.get('work_height',None),
                added_by=request.user)
            new_works.append(work)
            new_sources.append(src)
        elif src.rejection_reason is not None:
            continue
        else:
            work = src.media

        new_tag_instances.extend([TagWorkInstance(work=work, work_tag=TagWork.objects.get_or_create(name=t)[0]) for t in vid_info['tags']])
        pool_items.append(PoolItem(work=work, description='', pool=list_))

        i += 1

    list_.save()
    MediaWork.objects.bulk_create(new_works)
    TagWorkInstance.objects.bulk_create(new_tag_instances, ignore_conflicts=True) # bulk_create does not handle M2M so we do this manually
    WorkSource.objects.bulk_create(new_sources)
    PoolItem.objects.bulk_create(pool_items)
    return list_.id
