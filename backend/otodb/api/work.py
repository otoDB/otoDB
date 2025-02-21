from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router

from otodb.models import MediaWork

from .common import WorkSchema

work_router = Router()

def get_work_by_id(work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    if work.moved_to is not None:
        raise Exception('This work has been moved. Operation is invalid.')
    return work

@work_router.get('work', response=WorkSchema)
def work(request: HttpRequest, work_id: int):
    work = get_work_by_id(work_id)
    return work

