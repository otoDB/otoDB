from typing import List, Tuple

from django.urls import reverse
from ninja import NinjaAPI, Schema

from otodb.views.works import video_info
from otodb.models import WorkSource
from otodb.models.enums import Platform

api = NinjaAPI()

class VideoQuery(Schema):
    rel: str
    tags: List[Tuple[str, str]]

class Error(Schema):
    message: str

@api.get("/query_video", response={200: VideoQuery, 404: Error})
def query_video(request, platform: str, id: str):
    try:
        work = WorkSource.objects.get(platform=Platform.from_str(platform), source_id=id)
    except WorkSource.DoesNotExist:
        return 404, {'message': 'Not in the database.'}

    media = work.media
    tags = list(media.tags.values_list('name', 'id'))

    return {
        'tags': [(name, reverse('otodb:tag', kwargs={ 'tag_id': id_ })) for name, id_ in tags],
        'rel': reverse('otodb:work', kwargs={ 'work_id': media.id })
        }
