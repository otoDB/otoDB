from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.pagination import paginate

from otodb.models import Pool

from .common import ListSchema, ListItemSchema

list_router = Router()

@list_router.get('list', response=ListSchema)
def list(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    return list_

@list_router.get('entries', response=List[ListItemSchema])
@paginate
def entries(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    return list_.poolitem_set.order_by('order')
