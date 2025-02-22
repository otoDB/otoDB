from typing import List, Tuple

from django.urls import reverse

from ninja import NinjaAPI, Schema

from otodb.models import WorkSource
from otodb.models.enums import Platform

from .common import Error
from .auth import auth_router
from .work import work_router
from .profile import profile_router
from .list import list_router

api = NinjaAPI(urls_namespace="otodb:api", csrf=True)
api.add_router('/auth/', auth_router)
api.add_router('/work/', work_router)
api.add_router('/profile/', profile_router)
api.add_router('/list/', list_router)

class VideoQuery(Schema):
    rel: str
    tags: List[Tuple[str, str]]

@api.get("/query_video", response={ 200: VideoQuery, 404: Error })
def query_video(request, platform: str, id: str):
    try:
        work = WorkSource.objects.get(platform=Platform.from_str(platform), source_id=id)
    except WorkSource.DoesNotExist:
        return 404, {'message': 'Not in the database.'}

    media = work.media
    tags = list(media.tags.values_list('name', 'slug'))

    return {
        'tags': [(name, reverse('otodb:tag', kwargs={ 'tag_slug': slug })) for name, slug in tags],
        'rel': reverse('otodb:work', kwargs={ 'work_id': media.id })
        }
