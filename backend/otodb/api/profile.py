from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.security import django_auth

from otodb.account.models import Account

from .common import ListSchema, ProfileSchema

profile_router = Router()

@profile_router.get('profile', response=ProfileSchema)
def profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return user

@profile_router.get('lists', response=List[ListSchema])
def lists(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return user.pool_set

@profile_router.get('work_in_my_lists', response=List[tuple[ListSchema, bool]], auth=django_auth)
def work_in_lists(request: HttpRequest, work_id: int):
    return [(lst, lst.work_in_pool(work_id).exists()) for lst in request.user.pool_set.all()]
