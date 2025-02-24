from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router, Schema, ModelSchema

from otodb.models import MediaWork, WorkRelation

from .common import WorkSchema,WorkSourceSchema

work_router = Router()

@work_router.get('work', response=WorkSchema)
def work(request: HttpRequest, work_id: int):
    work = MediaWork.active_objects.get(id=work_id)
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
    class Meta:
        model = WorkRelation
        fields = ['relation']

@work_router.get('relations', response=tuple[list[WorkRelationSchema], list[SlimWorkSchema]])
def relations(request: HttpRequest, work_id: int):
    work = MediaWork.active_objects.get(id=work_id)
    relations, works = WorkRelation.get_component_from_work(work)
    return 200, (relations, works)

@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: HttpRequest, work_id: int):
    work = MediaWork.active_objects.get(id=work_id)
    return work.worksource_set
