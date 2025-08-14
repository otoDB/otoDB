from typing import Literal

from datetime import datetime

from django.http import HttpRequest
from django.contrib.contenttypes.models import ContentType

from simple_history.utils import update_change_reason

from ninja import Router, Schema
from ninja.pagination import paginate

from .common import ProfileSchema

history_router = Router()

class HistorySchema(Schema):
    history_id: int
    history_date: datetime
    history_user: ProfileSchema
    history_change_reason: str | None

@history_router.get('history',
    response=list[HistorySchema]
)
@paginate
def history(request: HttpRequest, pk: int, model: Literal['mediawork', 'mediasong', 'tagwork', 'tagsong', 'wikipage']):
    return ContentType.objects.get(model=model).model_class().history.filter(id=pk).order_by('-history_date')
