from typing import List, Tuple

from django.urls import reverse
from ninja import NinjaAPI, Schema

from otodb.views.works import video_info
from otodb.models import WorkSource

api = NinjaAPI()

class TagList(Schema):
    tags: List[Tuple[str, str]]

class Error(Schema):
    message: str

@api.get("/query_video", response={200: TagList, 404: Error})
def query_video(request, url: str):
    try:
        info = video_info(url)
    except Exception as e:
        print(e)
        return 404, {'message': 'Request failed'}

    if info['site'] is None:
        return 404, {'message': 'Site not supported'}

    work = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
        
    if work is None:
        return 404, {'message': 'Not in the database.'}
    
    tags = list(work.media.tags.values_list('name', 'id'))

    return {'tags': [(name, reverse('otodb:tag', kwargs={ 'tag_id': id_ })) for name, id_ in tags]}
