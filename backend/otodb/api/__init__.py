from django.contrib.admin.views.decorators import staff_member_required

from ninja import NinjaAPI

from .auth import auth_router
from .work import work_router
from .profile import profile_router
from .list import list_router
from .tag import tag_router
from .post import post_router

api = NinjaAPI(urls_namespace="otodb:api", csrf=True, docs_decorator=staff_member_required)
api.add_router('/auth/', auth_router)
api.add_router('/work/', work_router)
api.add_router('/profile/', profile_router)
api.add_router('/list/', list_router)
api.add_router('/tag/', tag_router)
api.add_router('/post/', post_router)

@api.get('stats')
def statistics(request):
    from otodb.models import MediaWork, TagWork, MediaSong, Pool
    return [
        MediaWork.active_objects.count(),
        TagWork.objects.count(),
        MediaSong.objects.count(),
        Pool.objects.count()
    ]
