from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router

from otodb.account.models import Account

from .common import ListSchema, ProfileSchema

profile_router = Router()

@profile_router.get('profile', response=ProfileSchema)
def profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return user

@profile_router.get('lists', response=list[ListSchema])
def lists(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return user.pool_set
