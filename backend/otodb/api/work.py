from datetime import date
from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Q

from simple_history.utils import update_change_reason

from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import video_info
from otodb.models import MediaWork, WorkRelation, WorkSource
from otodb.models.enums import WorkOrigin, Platform

from .common import WorkSchema, WorkSourceSchema, Error, TagWorkSchema

work_router = Router()

class ExternalQuery(Schema):
    work_id: int
    tags: List[TagWorkSchema]

@work_router.get('query_external', response=ExternalQuery)
def query_external(request: HttpRequest, platform: str, id: str):
    work = get_object_or_404(WorkSource, platform=Platform.from_str(platform), source_id=id)
    return { 'tags': work.media.tags, 'work_id': work.media.id }

@work_router.get('search', response=List[WorkSchema])
@paginate
def search(request: HttpRequest, query: str):
    return MediaWork.active_objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

@work_router.get('work', response=WorkSchema)
def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    return work

@work_router.get('random', response=WorkSchema)
def random(request: HttpRequest):
    return MediaWork.active_objects.random()

class IDSchema(Schema):
    id: int

class SlimWorkSchema(ModelSchema):
    class Meta:
        model = MediaWork
        fields = ['id', 'title', 'thumbnail']

class WorkRelationSchema(ModelSchema):
    A: IDSchema
    B: IDSchema
    id: int | None
    class Meta:
        model = WorkRelation
        fields = ['relation']

@work_router.get('relations', response=tuple[list[WorkRelationSchema], list[SlimWorkSchema]])
def relations(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    relations, works = WorkRelation.get_component_from_work(work)
    return 200, (relations, works)

@work_router.post('relation', auth=django_auth)
def create_relation(request: HttpRequest, payload: WorkRelationSchema):
    rel = WorkRelation.create(A_id=payload.A.id, B_id=payload.B.id, relation=payload.relation)
    return rel.id

@work_router.put('relation', auth=django_auth)
def update_relation(request: HttpRequest, payload: WorkRelationSchema):
    if payload.id is None:
        return 400
    rel = get_object_or_404(WorkRelation, id=payload.id)
    rel.A = get_object_or_404(MediaWork.active_objects, id=payload.A.id)
    rel.B = get_object_or_404(MediaWork.active_objects, id=payload.B.id)
    rel.relation = payload.relation
    rel.save()
    return

@work_router.delete('relation', auth=django_auth)
def delete_relation(request: HttpRequest, relation_id: int):
    rel = get_object_or_404(WorkRelation, id=relation_id)
    rel.delete()
    return

@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    return work.worksource_set

@work_router.post('refresh_source', auth=django_auth)
def refresh_source(request: HttpRequest, source_id: int):
    src = get_object_or_404(WorkSource, id=source_id)
    src.refresh()
    return

class WorkEditSchema(ModelSchema):
    works: tuple[int, int]
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'thumbnail', 'rating']

@work_router.post('merge', auth=django_auth)
def merge_works(request:HttpRequest, from_work_id: int, to_work_id: int, payload: WorkEditSchema):
    MediaWork.merge(
        get_object_or_404(MediaWork.active_objects, id=to_work_id),
        get_object_or_404(MediaWork.active_objects, id=from_work_id),
        payload.title,
        payload.description,
        payload.thumbnail,
        payload.rating
    )
    return

@work_router.put('work', auth=django_auth)
def update_work(request: HttpRequest, work_id: int, payload: WorkEditSchema, reason: str):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    for attr, value in payload.dict().items():
        setattr(work, attr, value)
    work.save()
    update_change_reason(work, reason)
    return

@work_router.post('source', auth=django_auth, response={200: int, 400: Error})
def new_source_from_url(request: HttpRequest, url: str, is_reupload: bool):
    info = video_info(url)
    if info['site'] is None:
        return 400, {'message': 'Site not supported'}

    try:
        src = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
    except WorkSource.DoesNotExist:
        src = WorkSource(media=None, title=info['title'], description=info['description'],
            url=info['url'], platform=info['site'], source_id=info['id'],
            published_date=date.fromtimestamp(info['timestamp']),
            work_origin=WorkOrigin(is_reupload), thumbnail=info.get('thumb', None),
            work_width=info.get('work_width', None), work_height=info.get('work_height', None))
        src.save()

    return src.id

@work_router.post('assign_source', auth=django_auth, description='Pass in work_id=-1 if creating new work from source.', response=int)
def assign_source_to_work(request: HttpRequest, source_id: int, work_id: int):
    src = get_object_or_404(WorkSource, id=source_id)
    info = video_info(src.url) # Hopefully still available!
    
    if work_id != -1:
        work = get_object_or_404(MediaWork.active_objects, id=work_id)
    else:
        work = MediaWork.objects.create(title=src.title, description=src.description, thumbnail=src.thumbnail)
    
    work.tags.add(*info.get('tags', []))

    src.media = work
    src.save()
    return work.id
