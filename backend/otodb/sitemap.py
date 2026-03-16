from datetime import datetime, timezone
from typing import Any, Callable, NotRequired, TypedDict

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import DateTimeField, Max, Model, OuterRef, QuerySet, Subquery
from django.db.models.functions import Coalesce, Greatest
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from otodb.account.models import Account
from otodb.models import MediaWork, TagWork, TagSong, Pool, Post
from otodb.models.posts import PostContent
from otodb.models.revision import RevisionChange

CHUNK_SIZE = 10_000


class SitemapTypeConfig(TypedDict):
	model: type[Model]
	filters: dict[str, Any]
	url_pattern: str
	value_field: str
	date_field: NotRequired[str | None]
	date_annotation: NotRequired[Callable]
	use_revision_date: NotRequired[bool]


SITEMAP_TYPES: dict[str, SitemapTypeConfig] = {
	'works': {
		'model': MediaWork,
		'filters': {'moved_to__isnull': True},
		'url_pattern': '/work/{value}',
		'value_field': 'id',
		'use_revision_date': True,
	},
	'tags': {
		'model': TagWork,
		'filters': {'aliased_to__isnull': True, 'deprecated': False},
		'url_pattern': '/tag/{value}',
		'value_field': 'slug',
		'use_revision_date': True,
	},
	'song_attributes': {
		'model': TagSong,
		'filters': {'aliased_to__isnull': True},
		'url_pattern': '/song_attribute/{value}',
		'value_field': 'slug',
		'use_revision_date': True,
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
		'date_annotation': lambda: Greatest(
			Subquery(
				PostContent.objects.filter(post_id=OuterRef('id'))
				.order_by('-modified')
				.values('modified')[:1]
			),
			Coalesce(
				'edited_at',
				datetime.fromtimestamp(0, tz=timezone.utc),
				output_field=DateTimeField(),
			),
		),
	},
	'profiles': {
		'model': Account,
		'filters': {'is_active': True},
		'url_pattern': '/profile/{value}',
		'value_field': 'username',
		'date_field': 'date_created',
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


def _annotate_lastmod(
	config: SitemapTypeConfig,
	queryset: QuerySet[Model],
) -> tuple[QuerySet[Model], bool]:
	if config.get('use_revision_date'):
		ct = ContentType.objects.get_for_model(config['model'])
		latest_rev = Subquery(
			RevisionChange.objects.filter(
				target_type=ct,
				target_id=OuterRef('pk'),
			)
			.order_by('-rev__date')
			.values('rev__date')[:1]
		)
		return queryset.annotate(lastmod=latest_rev), True

	date_annotation = config.get('date_annotation')
	if date_annotation:
		return queryset.annotate(lastmod=date_annotation()), True

	date_field = config.get('date_field')
	if date_field:
		from django.db.models import F

		return queryset.annotate(lastmod=F(date_field)), True

	return queryset, False


def _build_urlset(
	domain: str,
	url_pattern: str,
	value_field: str,
	queryset: QuerySet[Model],
	page: int,
	has_lastmod: bool,
) -> str:
	lo = page * CHUNK_SIZE
	hi = (page + 1) * CHUNK_SIZE
	fields = [value_field, 'lastmod'] if has_lastmod else [value_field]
	rows = (
		queryset.filter(pk__gte=lo, pk__lt=hi)
		.prefetch_related(None)
		.values_list(*fields)
		.iterator()
	)

	lines: list[str] = [
		'<?xml version="1.0" encoding="UTF-8"?>',
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
	]
	for row in rows:
		if has_lastmod:
			value, lastmod = row
		else:
			value = row[0]
			lastmod = None
		loc = f'{domain}{url_pattern.format(value=value)}'
		if lastmod and isinstance(lastmod, datetime):
			lines.append(
				f'  <url><loc>{loc}</loc><lastmod>{lastmod.isoformat()}</lastmod></url>'
			)
		else:
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
		queryset, has_lastmod = _annotate_lastmod(config, queryset)
		xml = _build_urlset(
			domain,
			config['url_pattern'],
			config['value_field'],
			queryset,
			page,
			has_lastmod,
		)

	return HttpResponse(xml, content_type='application/xml')
