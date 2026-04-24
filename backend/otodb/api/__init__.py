from typing import Generator

import ninja
import orjson
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page
from ninja import NinjaAPI
from ninja.decorators import decorate_view
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

from .auth import auth_router
from .comment import comment_router
from .common import ApiError
from .history import history_router
from .list import list_router
from .moderation import moderation_router
from .post import post_router
from .profile import profile_router
from .requests import request_router
from .source import source_router
from .tag import tag_router
from .work import work_router


def flatten_properties(
	prop_name: str,
	prop_details: dict[str, any],
	prop_required: bool,
	definitions: dict[str, any],
) -> Generator[tuple[str, dict[str, any], bool], None, None]:
	"""
	extracts all nested model's properties into flat properties
	(used f.e. in GET params with multiple arguments and models)
	"""
	if 'allOf' in prop_details:
		for item in prop_details['allOf']:
			if '$ref' in item:
				def_name = item['$ref'].rsplit('/', 1)[-1]
				definition = definitions.get(def_name, {})
				# Only resolve if it is NOT an Enum
				if 'enum' not in definition:
					item.update(definition)
					del item['$ref']
		# We check if it's a single-item allOf containing an enum-like structure
		if len(prop_details['allOf']) == 1 and '$ref' in prop_details['allOf'][0]:
			yield prop_name, prop_details, prop_required
		else:  # pragma: no cover
			# TODO: this code was for pydanitc 1.7+ ... <2.9 - check if this is still needed
			for item in prop_details['allOf']:
				yield from flatten_properties('', item, True, definitions, True)
	elif 'items' in prop_details and '$ref' in prop_details['items']:
		def_name = prop_details['items']['$ref'].rsplit('/', 1)[-1]
		prop_details['items'].update(definitions[def_name])
		del prop_details['items']['$ref']  # seems num data is there so ref not needed
		yield prop_name, prop_details, prop_required
	elif '$ref' in prop_details:
		def_name = prop_details['$ref'].split('/')[-1]
		definition = definitions.get(def_name, {})
		# If the target definition is an Enum, DO NOT flatten it. Yield as is.
		if 'enum' in definition:
			yield prop_name, prop_details, prop_required
		else:
			# Otherwise, continue standard flattening recursion
			yield from flatten_properties(
				prop_name, definition, prop_required, definitions
			)
	elif 'properties' in prop_details:
		required = set(prop_details.get('required', []))
		for k, v in prop_details['properties'].items():
			is_required = k in required
			yield from flatten_properties(k, v, is_required, definitions)
	else:
		yield prop_name, prop_details, prop_required


# Monkeypatch GET params to not inline schemas
ninja.openapi.schema.flatten_properties = flatten_properties


class ORJSONParser(Parser):
	def parse_body(self, request):
		return orjson.loads(request.body)


class ORJSONRenderer(BaseRenderer):
	media_type = 'application/json'

	def render(self, request, data, *, response_status):
		return orjson.dumps(data)


class WriteThrottle(AuthRateThrottle):
	"""Throttle mutating methods. Keyed by user, falls back to IP."""

	scope = 'write'
	WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

	def allow_request(self, request):
		if request.method not in self.WRITE_METHODS:
			return True
		return super().allow_request(request)


api = NinjaAPI(
	urls_namespace='otodb:api',
	docs_decorator=staff_member_required if settings.OTODB_PROTECT_API_DOCS else None,
	parser=ORJSONParser(),
	renderer=ORJSONRenderer(),
	throttle=[
		WriteThrottle('5/s'),
		AnonRateThrottle('20/s'),
		AuthRateThrottle('40/s'),
	],
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
api.add_router('/moderation/', moderation_router)


@api.exception_handler(ApiError)
def _handle_api_error(request, exc: ApiError):
	body: dict = {'code': exc.code}
	if exc.data is not None:
		body['data'] = exc.data
	return api.create_response(request, body, status=exc.status)


@api.get('stats', response=tuple[int, int, int, int])
@decorate_view(cache_page(60))
def statistics(request):
	from otodb.models import MediaSong, MediaWork, Pool, TagWork

	return [
		MediaWork.objects.filter(moved_to__isnull=True).count(),
		TagWork.objects.count(),
		MediaSong.objects.count(),
		Pool.objects.count(),
	]
