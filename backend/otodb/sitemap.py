from typing import Any, TypedDict

from django.conf import settings
from django.db.models import Max, Model, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from otodb.account.models import Account
from otodb.models import MediaWork, TagWork, TagSong, Pool, Post

CHUNK_SIZE = 10_000


class SitemapTypeConfig(TypedDict):
	model: type[Model]
	filters: dict[str, Any]
	url_pattern: str
	value_field: str


SITEMAP_TYPES: dict[str, SitemapTypeConfig] = {
	'works': {
		'model': MediaWork,
		'filters': {'moved_to__isnull': True},
		'url_pattern': '/work/{value}',
		'value_field': 'id',
	},
	'tags': {
		'model': TagWork,
		'filters': {'aliased_to__isnull': True, 'deprecated': False},
		'url_pattern': '/tag/{value}',
		'value_field': 'slug',
	},
	'song_attributes': {
		'model': TagSong,
		'filters': {'aliased_to__isnull': True},
		'url_pattern': '/song_attribute/{value}',
		'value_field': 'slug',
	},
	'lists': {
		'model': Pool,
		'filters': {},
		'url_pattern': '/list/{value}',
		'value_field': 'id',
	},
	'posts': {
		'model': Post,
		'filters': {},
		'url_pattern': '/post/{value}',
		'value_field': 'id',
	},
	'profiles': {
		'model': Account,
		'filters': {'is_active': True},
		'url_pattern': '/profile/{value}',
		'value_field': 'username',
	},
}


def _build_sitemap_index(
	domain: str,
	sitemap_url: str,
	sitemap_type: str,
	queryset: QuerySet[Model],
) -> str:
	max_id: int = queryset.aggregate(Max('pk'))['pk__max'] or 0
	num_pages = (max_id // CHUNK_SIZE) + 1

	lines: list[str] = [
		'<?xml version="1.0" encoding="UTF-8"?>',
		'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
	]
	for page in range(num_pages):
		lo = page * CHUNK_SIZE
		hi = (page + 1) * CHUNK_SIZE
		if queryset.filter(pk__gte=lo, pk__lt=hi).exists():
			lines.append(
				f'  <sitemap><loc>{domain}{sitemap_url}?type={sitemap_type}&amp;page={page}</loc></sitemap>'
			)
	lines.append('</sitemapindex>')
	return '\n'.join(lines)


def _build_urlset(
	domain: str,
	url_pattern: str,
	value_field: str,
	queryset: QuerySet[Model],
	page: int,
) -> str:
	lo = page * CHUNK_SIZE
	hi = (page + 1) * CHUNK_SIZE
	values = (
		queryset.filter(pk__gte=lo, pk__lt=hi)
		.prefetch_related(None)
		.values_list(value_field, flat=True)
		.iterator()
	)

	lines: list[str] = [
		'<?xml version="1.0" encoding="UTF-8"?>',
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
	]
	for value in values:
		loc = f'{domain}{url_pattern.format(value=value)}'
		lines.append(f'  <url><loc>{loc}</loc></url>')
	lines.append('</urlset>')
	return '\n'.join(lines)


@require_GET
@cache_page(3600)
def sitemap(request: HttpRequest) -> HttpResponse:
	domain = f'https://{settings.OTODB_FRONTEND_DOMAIN}'
	sitemap_url = request.path

	sitemap_type = request.GET.get('type')
	if not sitemap_type or sitemap_type not in SITEMAP_TYPES:
		return HttpResponseBadRequest('Missing or invalid type parameter.')

	config = SITEMAP_TYPES[sitemap_type]
	queryset: QuerySet[Model] = config['model'].objects.filter(**config['filters'])

	page_param = request.GET.get('page')
	if page_param is None:
		xml = _build_sitemap_index(domain, sitemap_url, sitemap_type, queryset)
	else:
		try:
			page = int(page_param)
		except ValueError:
			return HttpResponseBadRequest('Invalid page parameter.')
		xml = _build_urlset(
			domain, config['url_pattern'], config['value_field'], queryset, page
		)

	return HttpResponse(xml, content_type='application/xml')
