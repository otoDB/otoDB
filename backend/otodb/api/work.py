from typing import List
import subprocess

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router

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

@work_router.get('relations', response=str)
def relations(request: HttpRequest, work_id: int):
    work = MediaWork.active_objects.get(id=work_id)
    relations, works = WorkRelation.get_component_from_work(work)
    d2 = '\n'.join(['direction: right'] + [f'''{w.id}: {w.title} {{
            shape: image
            icon: {w.thumbnail}
            link: http:../{w.id}
            {'''style: {
                font-color: red
            }''' if work.id == w.id else ''}
        }}''' for w in works] + [str(r) for r in relations]) # TODO temporary workaround https://github.com/terrastruct/d2/issues/2357
    d2_out = subprocess.run(['d2', '--dark-theme=200', '-b=false', '-'], input=d2, capture_output=True, text=True)
    d2_out.check_returncode()

    return str(d2_out.stdout[38:]) # skip <?xml ... ?>

@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: HttpRequest, work_id: int):
    work = MediaWork.active_objects.get(id=work_id)
    return work.worksource_set
