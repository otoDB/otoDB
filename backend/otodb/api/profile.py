from typing import List

from pydantic import field_validator

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.account.models import Account
from otodb.models import ProfileConnection

from .common import ListSchema, ProfileSchema, WorkSourceSchema, ConnectionSchema

profile_router = Router()

@profile_router.get('profile', response=ProfileSchema)
def profile(request: HttpRequest, username: str):
    user = get_object_or_404(Account, username__iexact=username)
    return user

@profile_router.get('lists', response=List[ListSchema])
def lists(request: HttpRequest, username: str):
    user = get_object_or_404(Account, username__iexact=username)
    return user.pool_set

@profile_router.get('connection', response=List[ConnectionSchema])
def connection(request: HttpRequest, username: str):
    user = get_object_or_404(Account, username__iexact=username)
    return user.profileconnection_set

@profile_router.put('connection', auth=django_auth)
def edit_connection(request: HttpRequest, username: str, payload: ConnectionSchema):
    stripped = payload.content_id.strip()
    assert(stripped != '')
    user = get_object_or_404(Account, username__iexact=username)
    if user != request.user:
        return 403
    ProfileConnection.objects.update_or_create(profile=user, site=payload.site,
        defaults={ 'content_id': stripped })

@profile_router.delete('connection', auth=django_auth)
def delete_connection(request: HttpRequest, username: str, site: int):
    user = get_object_or_404(Account, username__iexact=username)
    if user.id != request.user.id:
        return 403
    ProfileConnection.objects.filter(profile=user, site=site).delete()

@profile_router.get('work_in_my_lists', response=List[tuple[ListSchema, bool]], auth=django_auth)
def work_in_lists(request: HttpRequest, work_id: int):
    return [(lst, lst.work_in_pool(work_id).exists()) for lst in request.user.pool_set.all()]

class SourceSubmissionSchema(WorkSourceSchema):
    media: int | None
    @field_validator("media", mode="before", check_fields=False)
    @classmethod
    def work_id(cls, value) -> str:
        return value.id if value is not None else None

@profile_router.get('submissions', response=List[SourceSubmissionSchema])
@paginate
def submissions(request: HttpRequest, username: str):
    user = get_object_or_404(Account, username__iexact=username)
    return user.worksource_set.all()
