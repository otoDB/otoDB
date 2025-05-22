from typing import List

from pydantic import field_validator

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.account.models import Account

from .common import ListSchema, ProfileSchema, WorkSourceSchema

profile_router = Router()

@profile_router.get('profile', response=ProfileSchema)
def profile(request: HttpRequest, username: str):
    user = get_object_or_404(Account, username__iexact=username)
    return user

@profile_router.get('lists', response=List[ListSchema])
def lists(request: HttpRequest, username: str):
    user = get_object_or_404(Account, username__iexact=username)
    return user.pool_set

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
