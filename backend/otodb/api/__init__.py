import orjson

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page

from ninja import NinjaAPI
from ninja.decorators import decorate_view
from ninja.parser import Parser
from ninja.renderers import BaseRenderer

from .auth import auth_router
from .work import work_router
from .source import source_router
from .profile import profile_router
from .list import list_router
from .tag import tag_router
from .post import post_router
from .comment import comment_router
from .history import history_router
from .requests import request_router


class ORJSONParser(Parser):
	def parse_body(self, request):
		return orjson.loads(request.body)


class ORJSONRenderer(BaseRenderer):
	media_type = 'application/json'

	def render(self, request, data, *, response_status):
		return orjson.dumps(data)


api = NinjaAPI(
	urls_namespace='otodb:api',
	docs_decorator=staff_member_required if settings.OTODB_PROTECT_API_DOCS else None,
	parser=ORJSONParser(),
	renderer=ORJSONRenderer(),
)
api.add_router('/auth/', auth_router)
api.add_router('/work/', work_router)
api.add_router('/upload/', source_router)
api.add_router('/profile/', profile_router)
api.add_router('/list/', list_router)
api.add_router('/tag/', tag_router)
api.add_router('/post/', post_router)
api.add_router('/comment/', comment_router)
api.add_router('/history/', history_router)
api.add_router('/request/', request_router)


@api.get('stats')
@decorate_view(cache_page(60))
def statistics(request):
	from otodb.models import MediaWork, TagWork, MediaSong, Pool

	return [
		MediaWork.objects.filter(moved_to__isnull=True).count(),
		TagWork.objects.count(),
		MediaSong.objects.count(),
		Pool.objects.count(),
	]
