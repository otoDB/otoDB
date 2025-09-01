from datetime import datetime

from typing import Literal

from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType

from django.db.models import Window
from django.db.models.functions import Rank

from django_comments_xtd.models import XtdComment

from ninja import Router, Schema
from ninja.security import django_auth
from ninja.throttling import AuthRateThrottle

from otodb.account.models import Account
from .common import user_is_trusted, ProfileSchema

comment_router = Router()

models_with_comments = ['mediawork', 'account', 'pool', 'tagwork', 'tagsong', 'post']

class CommentSchema(Schema):
    id: int
    level: int
    user: ProfileSchema
    comment: str
    submit_date: datetime
    parent_id: int
    index: int

@comment_router.get('comments', response=list[CommentSchema])
def get(request: HttpRequest, model: Literal[*models_with_comments], pk: int):
    T = ContentType.objects.get(model=model)
    index = Window(
        expression=Rank(),
        order_by='submit_date',
    )
    # Use comprehension to force filter after annotate
    return [c for c in XtdComment.objects.filter(content_type=T, object_pk=pk).order_by('id').annotate(index=index) if not c.is_removed]

@comment_router.post('comment', auth=django_auth, throttle=[AuthRateThrottle('1/8s')])
@user_is_trusted
def post(request: HttpRequest, model: Literal[*models_with_comments], pk: int, comment: str, parent_id: int = 0):
    T = ContentType.objects.get(model=model)
    XtdComment.objects.create(
        content_type=T,
        object_pk=pk,
        site_id=1,
        user=request.user,
        comment=comment,
        parent_id=parent_id
    )

@comment_router.delete('comment', auth=django_auth)
@user_is_trusted
def delete(request: HttpRequest, model: Literal[*models_with_comments], pk: int, comment_id: int):
    T = ContentType.objects.get(model=model)
    comment = XtdComment.objects.get(
        content_type=T,
        object_pk=pk,
        site_id=1,
        id=comment_id
    )
    if request.user.level >= Account.Levels.ADMIN or comment.user == request.user:
        comment.is_removed = True
        comment.save()
    else:
        return 403
