from datetime import datetime
from enum import Enum

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Max, OuterRef, Q, Subquery
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Field, Query, Schema
from ninja.errors import HttpError
from ninja.security import django_auth

from otodb.common import slugify_tag
from otodb.models import MediaWork, Revision, TagWork, WikiPage
from otodb.models.enums import LanguageTypes, Route

from .common import (
	OtodbID,
	RouterWithRevision,
	user_is_mod,
	user_is_trusted,
	with_revision_route,
)


def _annotate_modified(qs):
	"""Annotate WikiPage queryset with `modified` from the latest Revision targeting it."""
	wikipage_ct = ContentType.objects.get_for_model(WikiPage)
	latest_rev = (
		Revision.objects.filter(
			revisionchange__target_type=wikipage_ct,
			revisionchange__target_id=OuterRef('pk'),
		)
		.order_by('-date')
		.values('date')[:1]
	)
	return qs.annotate(modified=Subquery(latest_rev))


wiki_router = RouterWithRevision()


class WikiKind(str, Enum):
	TAG = 'tag'
	WORK = 'work'
	DOCS = 'docs'


class WikiPageMDSchema(Schema):
	page: str
	lang: LanguageTypes
	title: str | None = None
	modified: datetime | None = None


class WikiPageEditSchema(Schema):
	lang: LanguageTypes = Field(..., gt=0)
	md: str


class WikiIndexRowSchema(Schema):
	kind: WikiKind
	key: str
	title: str
	last_edited_at: datetime | None = None
	langs: list[LanguageTypes]


class WikiIndexResponseSchema(Schema):
	items: list[WikiIndexRowSchema]
	count: int


def _row_to_index_item(row: dict) -> dict:
	"""Map a grouped `.values()` row to a WikiIndexRowSchema-shaped dict."""
	if row['tag_id'] is not None:
		kind, key, title = WikiKind.TAG, row['tag__slug'], row['tag__name']
	elif row['work_id'] is not None:
		kind = WikiKind.WORK
		key = str(row['work_id'])
		title = row['work__title'] or f'Work #{row["work_id"]}'
	else:
		kind, key, title = WikiKind.DOCS, row['slug'], row['title'] or row['slug']
	return {
		'kind': kind,
		'key': key,
		'title': title,
		'last_edited_at': row['last_edited_at'],
		'langs': sorted(row['langs']),
	}


@wiki_router.get('', response=WikiIndexResponseSchema)
def index(
	request: HttpRequest,
	q: str | None = None,
	kind: WikiKind | None = None,
	lang: list[int] | None = Query(None),
	limit: int = 20,
	offset: int = 0,
):
	qs = _annotate_modified(WikiPage.objects.all())

	if kind == WikiKind.TAG:
		qs = qs.filter(tag__isnull=False)
	elif kind == WikiKind.WORK:
		qs = qs.filter(work__isnull=False)
	elif kind == WikiKind.DOCS:
		qs = qs.filter(slug__isnull=False)

	if lang:
		qs = qs.filter(lang__in=lang)

	if q:
		qs = qs.filter(
			Q(page__icontains=q)
			| Q(title__icontains=q)
			| Q(tag__name__icontains=q)
			| Q(work__title__icontains=q)
			| Q(slug__icontains=q)
		)

	# Group by the entity each page is attached to (a row has exactly one of
	# tag/work/slug, so these columns are 1:1 with the entity), aggregating the
	# langs and the latest edit so each entity surfaces once. Sort + paginate in
	# the DB instead of materializing every WikiPage.
	groups = (
		qs.values('tag_id', 'tag__slug', 'tag__name', 'work_id', 'work__title', 'slug')
		.annotate(
			title=Max('title'),
			langs=ArrayAgg('lang'),
			last_edited_at=Max('modified'),
		)
		.order_by(F('last_edited_at').desc(nulls_last=True))
	)

	return {
		'items': [_row_to_index_item(row) for row in groups[offset : offset + limit]],
		'count': groups.count(),
	}


def _apply_wiki_edits(
	lookup: dict,
	payload: list[WikiPageEditSchema],
	create_extra: dict | None = None,
) -> None:
	create_kwargs = {**lookup, **(create_extra or {})}
	for item in payload:
		empty = item.md.strip() == ''
		try:
			wp = WikiPage.objects.get(lang=item.lang, **lookup)
			if empty:
				wp.delete()
			else:
				wp.page = item.md
				wp.save()
		except WikiPage.DoesNotExist:
			if not empty:
				WikiPage.objects.create(lang=item.lang, page=item.md, **create_kwargs)


@wiki_router.get('tag/{tag_slug}', auth=django_auth, response=list[WikiPageMDSchema])
def get_tag_wiki(request: HttpRequest, tag_slug: str):
	return _annotate_modified(WikiPage.objects.filter(tag__slug=tag_slug)).order_by(
		'lang'
	)


@wiki_router.post('tag/{tag_slug}', auth=django_auth)
@user_is_trusted
@transaction.atomic
@with_revision_route(Route.TAGWORK_EDIT_WIKI)
def edit_tag_wiki(
	request: HttpRequest, tag_slug: str, payload: list[WikiPageEditSchema]
):
	tag = get_object_or_404(TagWork, slug=slugify_tag(tag_slug))
	if tag.aliased_to:
		tag = tag.aliased_to
	_apply_wiki_edits({'tag': tag}, payload)


@wiki_router.get('work/{work_id}', auth=django_auth, response=list[WikiPageMDSchema])
def get_work_wiki(request: HttpRequest, work_id: OtodbID):
	return _annotate_modified(WikiPage.objects.filter(work_id=work_id)).order_by('lang')


@wiki_router.post('work/{work_id}', auth=django_auth)
@user_is_trusted
@transaction.atomic
@with_revision_route(Route.MEDIAWORK_EDIT_WIKI)
def edit_work_wiki(
	request: HttpRequest, work_id: OtodbID, payload: list[WikiPageEditSchema]
):
	work = get_object_or_404(MediaWork, pk=work_id)
	_apply_wiki_edits({'work': work}, payload)


@wiki_router.get('{page_slug}', response=list[WikiPageMDSchema])
def get_slug_wiki(request: HttpRequest, page_slug: str):
	return _annotate_modified(WikiPage.objects.filter(slug=page_slug)).order_by('lang')


@wiki_router.post('{page_slug}', auth=django_auth)
@user_is_mod
@transaction.atomic
@with_revision_route(Route.WIKI_EDIT)
def edit_slug_wiki(
	request: HttpRequest,
	page_slug: str,
	payload: list[WikiPageEditSchema],
	title: str | None = None,
):
	try:
		WikiPage._meta.get_field('slug').run_validators(page_slug)
	except ValidationError as e:
		raise HttpError(400, '; '.join(e.messages))

	existing = WikiPage.objects.filter(slug=page_slug).first()
	resolved_title = (title if title is not None else existing and existing.title) or ''
	if resolved_title.strip() == '':
		raise HttpError(400, 'Title cannot be empty')
	resolved_title = resolved_title.strip()

	# Title is shared across langs; keep all rows for this slug in sync.
	if existing is not None and resolved_title != existing.title:
		for row in WikiPage.objects.filter(slug=page_slug):
			row.title = resolved_title
			row.save()

	_apply_wiki_edits(
		{'slug': page_slug}, payload, create_extra={'title': resolved_title}
	)
