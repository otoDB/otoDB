from datetime import datetime
from enum import Enum

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Field, Query, Schema
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


def _kind_and_key(wp: WikiPage) -> tuple[WikiKind, str, str]:
	if wp.tag_id is not None:
		tag: TagWork = wp.tag
		return WikiKind.TAG, tag.slug, tag.name
	if wp.work_id is not None:
		work: MediaWork = wp.work
		return WikiKind.WORK, str(work.pk), work.title or f'Work #{work.pk}'
	return WikiKind.DOCS, wp.slug, wp.title or wp.slug


@wiki_router.get('', response=WikiIndexResponseSchema)
def index(
	request: HttpRequest,
	q: str | None = None,
	kind: WikiKind | None = None,
	lang: list[int] | None = Query(None),
	limit: int = 20,
	offset: int = 0,
):
	qs = _annotate_modified(WikiPage.objects.select_related('tag', 'work').all())

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

	# Group by (kind, key) so each entity surfaces once with its langs aggregated
	grouped: dict[tuple[WikiKind, str], dict] = {}
	for wp in qs:
		k, key, title = _kind_and_key(wp)
		bucket = grouped.setdefault(
			(k, key),
			{
				'kind': k,
				'key': key,
				'title': title,
				'last_edited_at': wp.modified,
				'langs': [],
			},
		)
		bucket['langs'].append(wp.lang)
		if wp.modified is not None and (
			bucket['last_edited_at'] is None or wp.modified > bucket['last_edited_at']
		):
			bucket['last_edited_at'] = wp.modified

	for bucket in grouped.values():
		bucket['langs'].sort()

	edited = sorted(
		(g for g in grouped.values() if g['last_edited_at'] is not None),
		key=lambda g: g['last_edited_at'],
		reverse=True,
	)
	never_edited = [g for g in grouped.values() if g['last_edited_at'] is None]
	all_groups = edited + never_edited

	return {
		'items': all_groups[offset : offset + limit],
		'count': len(all_groups),
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


@wiki_router.get('{page_slug}', auth=django_auth, response=list[WikiPageMDSchema])
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
	existing = WikiPage.objects.filter(slug=page_slug).first()
	if existing is None and title is None:
		from ninja.errors import HttpError

		raise HttpError(400, 'title is required when creating a new wiki page')
	resolved_title = title if title is not None else existing.title

	# Title is shared across langs; keep all rows for this slug in sync.
	if existing is not None and resolved_title != existing.title:
		for row in WikiPage.objects.filter(slug=page_slug):
			row.title = resolved_title
			row.save()

	_apply_wiki_edits(
		{'slug': page_slug}, payload, create_extra={'title': resolved_title}
	)
