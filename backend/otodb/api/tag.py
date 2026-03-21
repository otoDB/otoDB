from typing import Annotated, Literal, Dict, Optional
from itertools import groupby
from functools import reduce, wraps
import re
from urllib.parse import urlparse, parse_qs, unquote

from django.db import transaction, models
from django.db.models import Value, F, Q, Case, When, Count, OuterRef, Exists, Subquery
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, get_list_or_404

from pydantic import AfterValidator, field_validator
from ninja import ModelSchema, Schema, Query, Field
from ninja.security import django_auth
from ninja.pagination import paginate
from ninja.utils import contribute_operation_args

from otodb.common import clean_incoming_slug, clean_incoming_tag_name
from otodb.models import (
	TagWork,
	MediaWork,
	MediaSong,
	WikiPage,
	SongRelation,
	TagSong,
	TagSongLangPreference,
	TagWorkConnection,
	MediaSongConnection,
	TagWorkLangPreference,
	TagWorkMediaConnection,
	TagWorkCreatorConnection,
	TagWorkInstance,
	TagWorkParenthood,
)
from otodb.models.enums import (
	WorkTagCategory,
	LanguageTypes,
	SongConnectionTypes,
	TagWorkConnectionTypes,
	MediaConnectionTypes,
	Route,
	MediaType,
)

from .common import (
	TagWorkSchema,
	ThinWorkSchema,
	user_is_trusted,
	RelationSchema,
	post_relations,
	ConnectionSchema,
	ConnectionLookupResponse,
	profile_connection_parsers,
	make_alt_value_parser,
	re_to_parser,
	RouterWithRevision,
	with_revision_route,
	TagLangPreferenceSchema,
	Error,
)

tag_router = RouterWithRevision()


class FatTagWorkSchema(ModelSchema):
	id: int
	children: list[TagWorkSchema]
	song: Optional[SongSchema] = Field(None, alias='get_song')
	media_type: list[int] | None = None
	lang_prefs: list[TagLangPreferenceSchema]
	aliased_to: Optional[TagWorkSchema]

	class Meta:
		model = TagWork
		fields = ['name', 'slug', 'category', 'deprecated']

	@field_validator('media_type', mode='before', check_fields=False)
	@classmethod
	def types(cls, value: int | None) -> list[int] | None:
		return [r for r in MediaType if r & value] if value else None


class WikiPageSchema(ModelSchema):
	class Meta:
		model = WikiPage
		fields = ['page', 'lang']


class TagWorkDetailsSchema(Schema):
	paths: tuple[list[TagWorkSchema], Dict[str, list[str]]]
	wiki_page: list[WikiPageSchema]
	aliases: list[TagWorkSchema]
	primary_parent: str | None = None


class TagSongSchema(Schema):
	id: int
	children: list['TagSongSchema']
	name: str
	slug: str
	category: int
	lang_prefs: list[TagLangPreferenceSchema]


class TagSongDetailsSchema(Schema):
	tree: list[TagSongSchema]
	aliases: list[TagSongSchema]


class SongSchema(ModelSchema):
	id: int
	work_tag: str = Field(..., alias='work_tag.slug')
	tags: list[TagSongSchema]

	class Meta:
		model = MediaSong
		fields = ['title', 'bpm', 'variable_bpm', 'author']


def filter_tags_by_media_type(qs, media_type: list[int]):
	return qs.annotate(
		mt=F('media_type').bitand(reduce(lambda a, b: a | b, media_type))
	).filter(Q(mt__gt=0))


@tag_router.get('search', response=list[TagWorkSchema])
@paginate
def search(
	request: HttpRequest,
	query: str,
	resolve_aliases: bool = True,
	category: int | None = None,
	media_type: list[int] | None = Query(None),
	order: str = 'newest',
	deprecated_only: bool = False,
	hide_orphans: bool = True,
	wiki_lang: list[int] | None = Query(None),
	wiki_lang_missing: list[int] | None = Query(None),
	lang_pref: list[int] | None = Query(None),
	lang_pref_missing: list[int] | None = Query(None),
	has_connections: bool | None = None,
):
	cleaned_query = clean_incoming_tag_name(query)
	qs = TagWork.objects.filter(name__contains=cleaned_query)

	if resolve_aliases:
		qs = qs.filter(aliased_to__isnull=True) | TagWork.objects.filter(
			id__in=qs.values('aliased_to__id')
		)

	if category is not None and category != -1:
		qs = qs.filter(category=category)
		if category == WorkTagCategory.MEDIA and media_type:
			qs = filter_tags_by_media_type(qs, media_type)

	qs = qs.filter(deprecated=deprecated_only)
	qs = qs.annotate(
		n_instance=Case(
			When(aliased_to__isnull=False, then=Count('aliased_to__tagworkinstance')),
			default=Count('tagworkinstance'),
			output_field=models.IntegerField(),
		),
		_has_connections=Exists(TagWorkConnection.objects.filter(tag=OuterRef('pk')))
		| Exists(TagWorkMediaConnection.objects.filter(tag=OuterRef('pk')))
		| Exists(TagWorkCreatorConnection.objects.filter(tag=OuterRef('pk'))),
	)

	if hide_orphans:
		qs = qs.filter(n_instance__gt=0)

	wiki_sub = WikiPage.objects.filter(tag=OuterRef('pk'))
	pref_sub = TagWorkLangPreference.objects.filter(
		Q(tag=OuterRef('pk')) | Q(tag__aliased_to=OuterRef('pk'))
	)

	if wiki_lang:
		qs = qs.filter(Exists(wiki_sub.filter(lang__in=wiki_lang)))
	if wiki_lang_missing:
		qs = qs.filter(~Exists(wiki_sub.filter(lang__in=wiki_lang_missing)))

	if lang_pref:
		values = [v for v in lang_pref if v > 0]
		cond = Q()
		if values:
			cond |= Exists(pref_sub.filter(lang__in=values))
		if -1 in lang_pref:
			cond |= ~Exists(pref_sub)
		qs = qs.filter(cond)
	if lang_pref_missing:
		values = [v for v in lang_pref_missing if v > 0]
		cond = Q()
		if values:
			cond &= ~Exists(pref_sub.filter(lang__in=values))
		if -1 in lang_pref_missing:
			cond &= Exists(pref_sub)
		qs = qs.filter(cond)

	if has_connections is not None:
		qs = qs.filter(_has_connections=has_connections)

	order_field = {
		'newest': '-id',
		'count': '-n_instance',
		'name': 'name',
	}.get(order, '-id')

	if cleaned_query:
		qs = qs.annotate(
			exact_match=Case(
				When(name__iexact=cleaned_query, then=Value(0)),
				When(
					Exists(
						TagWork.objects.filter(
							id=OuterRef('id'), aliases__name__iexact=cleaned_query
						)
					),
					then=Value(1),
				),
				default=Value(99),
				output_field=models.IntegerField(),
			),
		).order_by('exact_match', order_field)
	else:
		qs = qs.order_by(order_field)

	return qs


@tag_router.get('tag', response={200: FatTagWorkSchema, 300: str})
def tag(request: HttpRequest, tag_slug: str):
	cleaned = clean_incoming_slug(tag_slug)
	tag = get_object_or_404(TagWork, slug=cleaned)
	# Check only after querying
	# want 404 without redirection if the cleaned doesn't exist either
	if cleaned != tag_slug:
		return 300, cleaned
	if tag.aliased_to:
		return 300, tag.aliased_to.slug
	return tag


@tag_router.get('details', response=TagWorkDetailsSchema)
def details(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(
		TagWork.objects.prefetch_related('childhood', 'wikipage_set'),
		slug=tag_slug,
	)

	primary_parent = [
		*tag.childhood.filter(primary=True).values_list('parent__slug', flat=True)
	]
	primary_parent = primary_parent[0] if primary_parent else None

	paths = tag.get_paths().exclude(fr='')

	adj = {
		k: [vv[0] for vv in v]
		for k, v in groupby(
			paths.order_by('fr').values_list('slug', 'fr'), lambda x: x[1]
		)
	}
	return {
		'paths': (paths.distinct(), adj),
		'primary_parent': primary_parent,
		'wiki_page': tag.wikipage_set,
		'aliases': tag.aliases,
	}


@tag_router.get('works', response=list[ThinWorkSchema])
@paginate
def works(request: HttpRequest, tag_slug: str):
	return MediaWork.active_objects.filter(tags__slug=tag_slug)


def tag_route_switch(work_route: Route, song_route: Route):
	def decorator(f):
		@wraps(f)
		def wrapper(request, *args, **kwargs):
			type = kwargs.pop('type')
			kwargs['model'] = (
				(TagWork, TagWorkLangPreference)
				if type == 'work'
				else (TagSong, TagSongLangPreference)
			)
			return with_revision_route(work_route if type == 'work' else song_route)(f)(
				request,
				*args,
				**kwargs,
			)

		contribute_operation_args(
			wrapper,
			'type',
			Literal['work', 'song'],
			Query(default='work'),
		)

		return wrapper

	return decorator


class AliasResponse(Schema):
	merged_slug: str


@tag_router.post('alias', auth=django_auth, response=AliasResponse)
@user_is_trusted
@tag_route_switch(Route.TAGWORK_ALIAS, Route.SONGTAG_ALIAS)
def alias_tags(
	request: HttpRequest, from_tags: list[str], into_tag: str, delete: bool, **kwargs
):
	model, _ = kwargs['model']

	tags = []
	for tag_name in from_tags:
		try:
			tags.append(model.objects.get(slug=clean_incoming_slug(tag_name)))
		except model.DoesNotExist:
			tags.append(model.objects.create(name=tag_name))

	into = get_object_or_404(
		model.objects.select_related('aliased_to'), slug=clean_incoming_slug(into_tag)
	)
	if into.aliased_to:
		into = into.aliased_to
	assert into.aliased_to is None

	model.alias(tags, into)
	if delete:
		for tag in tags:
			tag.aliased_to = None
			tag.save()
			if tag.can_be_deleted:
				tag.delete()

	return AliasResponse(merged_slug=into.slug)


@tag_router.delete('tag', auth=django_auth, response={200: None, 400: None})
@user_is_trusted
@tag_route_switch(Route.TAGWORK_DELETE, Route.SONGTAG_DELETE)
def delete(request: HttpRequest, tag_slug: str, **kwargs):
	model, _ = kwargs['model']

	tag = get_object_or_404(model, slug=tag_slug)
	if tag.can_be_deleted:
		tag.delete()
	else:
		return 400, None


class TagAliasControlSchema(Schema):
	base_slug: str
	unalias_slugs: list[str]
	lang_prefs: dict[int, str | None]


@tag_router.post('tag_aliases', auth=django_auth)
@user_is_trusted
@tag_route_switch(Route.TAGWORK_UNALIAS, Route.SONGTAG_UNALIAS)
def tag_alias_control(
	request: HttpRequest, tag_slug: str, payload: TagAliasControlSchema, **kwargs
):
	model, model_lang_prefs = kwargs['model']

	tag = get_object_or_404(model, slug=tag_slug)

	assert tag.aliased_to is None
	assert payload.base_slug not in payload.unalias_slugs
	curr_aliases = [*tag.aliases.all()]

	curr_aliases_slugs = [t.slug for t in curr_aliases]
	assert payload.base_slug == tag.slug or payload.base_slug in curr_aliases_slugs
	assert all(
		[v == tag_slug or v in curr_aliases_slugs for v in payload.unalias_slugs]
	)

	curr_aliases_names = [t.name for t in curr_aliases]
	assert all(
		[
			v == tag.name or v in curr_aliases_names
			for v in payload.lang_prefs.values()
			if v is not None
		]
	)

	# unalias
	if payload.unalias_slugs:
		model.objects.filter(slug__in=payload.unalias_slugs).update(aliased_to=None)
	# They may be stale now, just requery
	del curr_aliases, curr_aliases_slugs, curr_aliases_names

	# lang prefs
	for lang, name in payload.lang_prefs.items():
		lang = LanguageTypes(lang).value
		assert lang != 0
		if name:
			tags_to_clear = list(tag.aliases.exclude(name=name))
			if name != tag.name:
				tags_to_clear.append(tag)
			model_lang_prefs.objects.filter(tag__in=tags_to_clear, lang=lang).delete()
			model_lang_prefs.objects.get_or_create(
				tag=model.objects.get(name=name), lang=lang
			)

	# set base
	if payload.base_slug != tag_slug:
		new_base = tag.aliases.get(slug=payload.base_slug)
		model.transfer_data(tag, new_base)

		tag.aliases.exclude(pk=new_base.pk).update(aliased_to=new_base)
		tag.aliased_to = None if tag_slug in payload.unalias_slugs else new_base
		tag.save()
		new_base.aliased_to = None
		new_base.save()


class WorkTagInSchema(Schema):
	category: int
	deprecated: bool
	parent_slugs: list[str]
	media_type: list[int] | None = None
	primary: int | None


class SongTagInSchema(Schema):
	parent_slug: str | None
	category: int


class SongInSchema(ModelSchema):
	class Meta:
		model = MediaSong
		fields = ['title', 'bpm', 'variable_bpm', 'author']


@tag_router.put('tag', auth=django_auth)
@user_is_trusted
@transaction.atomic
@with_revision_route(Route.TAGWORK_UPDATE)
def update(
	request: HttpRequest,
	tag_slug: str,
	payload: WorkTagInSchema,
	song_payload: SongInSchema | None = None,
):
	tag = get_object_or_404(
		TagWork.objects.select_for_update(of=('self',)), slug=tag_slug
	)
	if (
		tag.category == WorkTagCategory.SONG
		and payload.category != WorkTagCategory.SONG
	):
		tag.mediasong.delete()
	if payload.category == WorkTagCategory.SONG:
		song_payload.title = song_payload.title.strip()
		song_payload.author = song_payload.author.strip()
		assert song_payload.title
		assert song_payload.author
		try:
			song = tag.mediasong
			song.title = song_payload.title
			song.bpm = song_payload.bpm
			song.author = song_payload.author
			song.variable_bpm = song_payload.variable_bpm
			song.save()
		except MediaSong.DoesNotExist:
			tag.category = WorkTagCategory.SONG
			song = MediaSong.objects.create(work_tag=tag, **song_payload.dict())
	# If category changed from source to creator or media, mark all instances with used_as_source
	if tag.category == WorkTagCategory.SOURCE and payload.category in (
		WorkTagCategory.CREATOR,
		WorkTagCategory.MEDIA,
	):
		TagWorkInstance.objects.filter(work_tag=tag).update(used_as_source=True)

	# Remove creator connections if no longer a creator
	if (
		tag.category == WorkTagCategory.CREATOR
		and payload.category != WorkTagCategory.CREATOR
	):
		TagWorkCreatorConnection.objects.filter(tag=tag).delete()

	# Remove media connections and media type if no longer media
	if (
		tag.category == WorkTagCategory.MEDIA
		and payload.category != WorkTagCategory.MEDIA
	):
		TagWorkMediaConnection.objects.filter(tag=tag).delete()
		tag.set_media_type([])

	if payload.category == WorkTagCategory.MEDIA:
		if payload.media_type:
			tag.category = payload.category
			tag.set_media_type(payload.media_type)

	tag.deprecated = payload.deprecated
	tag.category = payload.category
	tag.save()

	ps = [
		get_object_or_404(TagWork, slug=s).aliased_to
		or get_object_or_404(TagWork, slug=s, aliased_to__isnull=True)
		for s in [clean_incoming_slug(p) for p in payload.parent_slugs]
	]
	assert payload.primary is None or 0 <= payload.primary < len(ps)
	tag.childhood.exclude(parent__in=ps).delete()
	desc = tag.get_descendants()
	for p in ps:
		if (
			not TagWorkParenthood.objects.filter(tag=tag, parent=p).exists()
			and p not in desc
		):
			TagWorkParenthood.objects.create(parent=p, tag=tag)
	if ps:
		tag.childhood.update(primary=False)
		if payload.primary is not None:
			tag.childhood.filter(parent=ps[payload.primary]).update(primary=True)

	return


class WikiPageMDSchema(ModelSchema):
	class Meta:
		model = WikiPage
		fields = ['page', 'lang']


@tag_router.get('wiki_page', auth=django_auth, response=list[WikiPageMDSchema])
def wiki_page(request: HttpRequest, tag_slug: str):
	pages = get_list_or_404(WikiPage, tag__slug=tag_slug)
	return pages


@tag_router.post('wiki_page', auth=django_auth)
@user_is_trusted
@with_revision_route(Route.TAGWORK_EDIT_WIKI)
def edit_wiki_page(request: HttpRequest, tag_slug: str, lang: int, md: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	empty = md.strip() == ''
	try:
		wp = WikiPage.objects.get(tag=tag, lang=LanguageTypes(lang).value)
		if empty:
			wp.delete()
		else:
			wp.page = md
			wp.save()
	except WikiPage.DoesNotExist:
		if not empty:
			WikiPage.objects.create(
				tag=tag,
				lang=LanguageTypes(lang).value,
				page=md,
			)


@tag_router.get(
	'connection', response=tuple[list[ConnectionSchema], list[ConnectionSchema] | None]
)
def connection(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	cs = tag.tagworkconnection_set.all()
	if tag.category == WorkTagCategory.MEDIA:
		return 200, (cs, tag.tagworkmediaconnection_set.all())
	elif tag.category == WorkTagCategory.CREATOR:
		return 200, (cs, tag.tagworkcreatorconnection_set.all().order_by('dead'))
	return 200, (cs, None)


def query_parser(param_arg: str, param_match=None):
	def match(link):
		try:
			parse = parse_qs(urlparse(link).query)[param_arg][0]
			if param_match is None or param_match(parse):
				return parse
		except Exception:
			pass

	return match


def parser_conjunction(parser, conditions):
	def match(link):
		if all(c(link) for c in conditions):
			return parser(link)

	return match


song_connection_parser = make_alt_value_parser(
	(
		SongConnectionTypes.VGMDB,
		re_to_parser(re.compile(r'https?:\/\/vgmdb\.net\/album\/(\d+)(?:\/*)?')),
	),
	(
		SongConnectionTypes.VOCADB,
		re_to_parser(re.compile(r'https?:\/\/vocadb\.net\/S\/(\d+)(?:\/*)?')),
	),
	(
		SongConnectionTypes.DISCOGS,
		re_to_parser(
			re.compile(r'https?:\/\/www\.discogs\.com\/master\/(\d+)(?:\/*)?')
		),
	),
	(
		SongConnectionTypes.MUSICBRAINZ,
		re_to_parser(
			re.compile(r'https?:\/\/musicbrainz\.org\/recording\/([a-f0-9-]+)(?:\/*)?')
		),
	),
	(
		SongConnectionTypes.RATEYOURMUSIC,
		re_to_parser(
			re.compile(r'https?:\/\/rateyourmusic\.com\/song\/([^/]+)(?:\/+)?')
		),
	),
	(
		SongConnectionTypes.DOJINMUSIC,
		re_to_parser(
			re.compile(r'https?:\/\/www.dojin-music\.info\/song\/(\d+)(?:\/+)?')
		),
	),
	(
		SongConnectionTypes.TOUHOUDB,
		re_to_parser(re.compile(r'https?:\/\/touhoudb\.com\/S\/(\d+)(?:\/*)?')),
	),
	(
		SongConnectionTypes.REMYWIKI,
		re_to_parser(re.compile(r'https?:\/\/remywiki\.com\/(.+?)(?:\/*)?')),
	),
	(
		SongConnectionTypes.SILENTBLUE,
		re_to_parser(
			re.compile(r'https?:\/\/silentblue\.remywiki\.com\/(.+?)(?:\/*)?')
		),
	),
	(
		SongConnectionTypes.ZENIUS,
		parser_conjunction(
			query_parser('songid', lambda s: s.isdigit()),
			[
				lambda link: re.compile(
					r'https?:\/\/zenius-i-vanisher\.com\/v5\.2\/songdb\.php'
				).match(link),
			],
		),
	),
	(
		SongConnectionTypes.NNDMEDLEYWIKI,
		re_to_parser(re.compile(r'https?:\/\/medley\.bepis\.io\/wiki\/(.+?)(?:\/*)?')),
	),
	(
		SongConnectionTypes.MODARCHIVE,
		parser_conjunction(
			query_parser('query', lambda s: s.isdigit()),
			[
				lambda link: query_parser('request')(link) == 'view_by_moduleid',
				lambda link: re.compile(r'https?:\/\/modarchive\.org\/index.php').match(
					link
				),
			],
		),
	),
)

tag_work_connection_parser = make_alt_value_parser(
	(
		TagWorkConnectionTypes.OTOMADWIKI,
		re_to_parser(re.compile(r'https?:\/\/otomad\.wiki\/([^/?#]+)\/?')),
	),
	(
		TagWorkConnectionTypes.OTOMADFANDOM,
		re_to_parser(
			re.compile(r'https?:\/\/otomad\.fandom\.com\/ja\/wiki\/([^/?#]+)\/?')
		),
	),
	(
		TagWorkConnectionTypes.NICOPEDIA,
		re_to_parser(
			re.compile(r'https?:\/\/dic\.nicovideo\.jp\/((?:a|v)\/[^/?#]+)\/?')
		),
	),
	(
		TagWorkConnectionTypes.PIXIV_DICT,
		re_to_parser(re.compile(r'https?:\/\/dic\.pixiv\.net\/a\/([^/?#]+)\/?')),
	),
	(
		TagWorkConnectionTypes.WIKIPEDIA,
		re_to_parser(re.compile(r'https?:\/\/en\.wikipedia\.org\/wiki\/([^/?#]+)\/?')),
	),
	(
		TagWorkConnectionTypes.NAMUWIKI,
		re_to_parser(
			re.compile(r'https?:\/\/(?:[a-z]{2,}\.)?namu\.wiki\/w\/([^/?#]+)\/?')
		),
	),
	(
		TagWorkConnectionTypes.KNOWYOURMEME,
		re_to_parser(re.compile(r'https?:\/\/knowyourmeme\.com\/([^?#]+)\/?')),
	),
)

media_connection_parser = make_alt_value_parser(
	(
		MediaConnectionTypes.ANIKORE,
		re_to_parser(re.compile(r'https?:\/\/www\.anikore\.jp\/anime\/(\d+)\/?')),
	),
	(
		MediaConnectionTypes.BANGUMI,
		re_to_parser(re.compile(r'https?:\/\/bangumi\.tv\/subject\/(\d+)\/?')),
	),
	(
		MediaConnectionTypes.ANIDB,
		re_to_parser(re.compile(r'https?:\/\/anidb\.net\/anime\/(\d+)\/?')),
	),
	(
		MediaConnectionTypes.MYANIMELIST,
		re_to_parser(re.compile(r'https?:\/\/myanimelist\.net\/anime\/(\d+)\/?')),
	),
	(
		MediaConnectionTypes.ANILIST,
		re_to_parser(re.compile(r'https?:\/\/anilist\.co\/anime\/(\d+)\/?')),
	),
	(
		MediaConnectionTypes.KITSU,
		re_to_parser(re.compile(r'https?:\/\/kitsu\.io\/anime\/([^/?#]+)\/?')),
	),
	(
		MediaConnectionTypes.ANIMEPLANET,
		re_to_parser(
			re.compile(r'https?:\/\/www\.anime-planet\.com\/anime\/([^/?#]+)\/?')
		),
	),
	(
		MediaConnectionTypes.IMDB,
		re_to_parser(re.compile(r'https?:\/\/www\.imdb\.com\/title\/(\d+)\/?')),
	),
	(
		MediaConnectionTypes.LETTERBOXD,
		re_to_parser(re.compile(r'https?:\/\/letterboxd\.com\/film\/([^/?#]+)\/?')),
	),
	(
		MediaConnectionTypes.VNDB,
		re_to_parser(re.compile(r'https?:\/\/vndb\.org\/(v\d+)\/?')),
	),
	(
		MediaConnectionTypes.EROGAMESCAPE,
		parser_conjunction(
			query_parser('game', lambda s: s.isdigit()),
			[
				lambda link: re.compile(
					r'https?:\/\/erogamescape\.dyndns\.org\/~ap2\/ero\/toukei_kaiseki\/game\.php'
				).match(link),
			],
		),
	),
	(
		MediaConnectionTypes.VGMDB,
		re_to_parser(re.compile(r'https?:\/\/vgmdb\.net\/product\/(\d+)\/?')),
	),
)


def make_dead_link_parser(parser):
	def match(link):
		dead = link.startswith('-')
		parse = parser(link[1:] if dead else link)
		return (dead, parse) if parse else None

	return match


creator_tag_connection_parser = make_alt_value_parser(
	*[(v, make_dead_link_parser(parser)) for v, parser in profile_connection_parsers]
)


@tag_router.put('connection', auth=django_auth)
@user_is_trusted
@with_revision_route(Route.TAGWORK_EDIT_CONNECTIONS)
def edit_connections(request: HttpRequest, tag_slug: str, urls: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	category_parser_tp = {
		WorkTagCategory.SONG: (MediaSongConnection, song_connection_parser),
		WorkTagCategory.MEDIA: (TagWorkMediaConnection, media_connection_parser),
		WorkTagCategory.CREATOR: (
			TagWorkCreatorConnection,
			creator_tag_connection_parser,
		),
	}.get(tag.category, (None, lambda _: None))
	total_parser = make_alt_value_parser(
		(TagWorkConnection, tag_work_connection_parser), category_parser_tp
	)
	urls = [total_parser(url) for url in urls.split('\n') if url.strip()]
	urls = [url for url in urls if url]
	general_con = [url for tp, url in urls if tp is TagWorkConnection]
	category_con = [url for tp, url in urls if tp is not TagWorkConnection]

	# Category specific connections
	Table = category_parser_tp[0]
	if Table is not None:

		def get_content_dict(parse):
			return (
				{'content_id': parse[1], 'dead': parse[0]}
				if Table is TagWorkCreatorConnection
				else {'content_id': parse}
			)

		target = (
			{'song': tag.mediasong}
			if tag.category == WorkTagCategory.SONG
			else {'tag': tag}
		)
		Table.objects.filter(**target).exclude(
			reduce(
				lambda a, b: a | b,
				[
					Q(site=site) & Q(content_id=get_content_dict(parse)['content_id'])
					for site, parse in category_con
				],
				Q(),
			)
		).delete()
		for site, parse in category_con:
			old = Table.objects.filter(
				**target, site=site, content_id=get_content_dict(parse)['content_id']
			)
			if not old.exists():
				Table.objects.create(**target, site=site, **get_content_dict(parse))
			elif Table is TagWorkCreatorConnection:
				old.update(dead=get_content_dict(parse)['dead'])

	# All general connections
	TagWorkConnection.objects.filter(tag=tag).exclude(
		reduce(
			lambda a, b: a | b,
			[
				Q(site=site) & Q(content_id=content_id)
				for site, content_id in general_con
			],
			Q(),
		)
	).delete()
	for site, content_id in general_con:
		old = TagWorkConnection.objects.filter(
			tag=tag, site=site, content_id=content_id
		)
		if not old.exists():
			TagWorkConnection.objects.create(site=site, content_id=content_id, tag=tag)


@tag_router.get('song', response=str)
def song(request: HttpRequest, id: int):
	return get_object_or_404(MediaSong, id=id).work_tag.slug


@tag_router.get('song_search', response=list[SongSchema])
@paginate
def song_search(
	request: HttpRequest,
	query: str,
	author: str,
	tags: str | None = None,
	bpm_range: tuple[int, int] | None = Query(None),
):
	cleaned_query = clean_incoming_tag_name(query)
	qs = MediaSong.objects.filter(
		Q(title__icontains=query)
		| Q(work_tag__name__icontains=cleaned_query)
		| Q(work_tag__aliases__name__icontains=cleaned_query),
		author__icontains=author,
		work_tag__aliased_to__isnull=True,
	).distinct()
	if tags:
		for tag in tags.split():
			tag_slug = clean_incoming_slug(tag)
			qs = qs.filter(Q(tags__slug=tag_slug) | Q(tags__aliases__slug=tag_slug))
	elif query.isdigit():
		qs = qs.annotate(priority=Value(100))
		qs = (
			MediaSong.objects.filter(id=int(query))
			.annotate(priority=Value(0))
			.union(qs)
		)
		qs = qs.order_by('priority')
	if bpm_range:
		qs = qs.filter(bpm__gte=bpm_range[0], bpm__lte=bpm_range[1])
	return qs


@tag_router.get(
	'song_relations', response=tuple[list[RelationSchema], list[SongSchema]]
)
def song_relations(request: HttpRequest, song_id: int):
	song = get_object_or_404(MediaSong.objects, id=song_id)
	relations = SongRelation.get_component(song.id)
	return 200, (relations, {s.id: s for r in relations for s in (r.A, r.B)}.values())


@tag_router.post('song_relation', auth=django_auth)
@with_revision_route(Route.SONGRELATION_CREATE)
@user_is_trusted
def song_relation(request: HttpRequest, this_id: int, payload: list[RelationSchema]):
	post_relations(MediaSong, this_id, payload)


@tag_router.get('song_tag_search', response=list[TagSongSchema])
@paginate
def song_tag_search(
	request: HttpRequest,
	query: str,
	resolve_aliases: bool = True,
	category: int | None = None,
):
	cleaned_query = clean_incoming_tag_name(query)
	qs = TagSong.objects.filter(name__contains=cleaned_query)

	if resolve_aliases:
		qs = qs.filter(aliased_to__isnull=True) | TagSong.objects.filter(
			id__in=qs.values('aliased_to__id')
		)

	if category is not None and category != -1:
		qs = qs.filter(category=category)

	return qs.annotate(
		n_instance=Case(
			When(aliased_to__isnull=False, then=Count('aliased_to__tagsonginstance')),
			default=Count('tagsonginstance'),
			output_field=models.IntegerField(),
		),
		exact_match=Case(
			When(name__iexact=cleaned_query, then=Value(0)),
			When(
				Exists(
					TagSong.objects.filter(
						id=OuterRef('id'), aliases__name__iexact=cleaned_query
					)
				),
				then=Value(1),
			),
			default=Value(99),
			output_field=models.IntegerField(),
		),
	).order_by('exact_match', '-n_instance')


@tag_router.post('song_tags', auth=django_auth)
@user_is_trusted
@with_revision_route(Route.MEDIASONG_SET_TAGS)
def song_tags(
	request: HttpRequest,
	song_id: int,
	tags: list[Annotated[str, AfterValidator(clean_incoming_tag_name)]],
):
	song = get_object_or_404(MediaSong.objects, id=song_id)
	song.tags.set(tags)
	return


@tag_router.get('song_tag', response={200: TagSongSchema, 300: str})
def song_tag(request: HttpRequest, tag_slug: str):
	cleaned = clean_incoming_slug(tag_slug)
	tag = get_object_or_404(TagSong, slug=cleaned)
	# Check only after querying
	# want 404 without redirection if the cleaned doesn't exist either
	if cleaned != tag_slug:
		return 300, cleaned
	if tag.aliased_to:
		return 300, tag.aliased_to.slug
	return tag


@tag_router.get('song_tag_details', response=TagSongDetailsSchema)
def song_tag_details(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagSong, slug=tag_slug)
	return {
		'tree': list(tag.get_tree())[:-1],
		'aliases': tag.aliases,
	}


@tag_router.put('song_tag', auth=django_auth)
@user_is_trusted
@transaction.atomic
@with_revision_route(Route.SONGTAG_UPDATE)
def update_song_tag(request: HttpRequest, tag_slug: str, payload: SongTagInSchema):
	tag = get_object_or_404(
		TagSong.objects.select_for_update(of=('self',)), slug=tag_slug
	)
	tag.category = payload.category
	if payload.parent_slug:
		parent = get_object_or_404(TagSong, slug=payload.parent_slug)
		assert all(tag.id != t.id for t in parent.get_tree())
		tag.parent = parent
	else:
		tag.parent = None
	tag.save()
	return


@tag_router.get('songs', response=list[SongSchema])
@paginate
def songs(request: HttpRequest, tag_slug: str):
	return MediaSong.objects.filter(tags__slug=tag_slug)


@tag_router.get('song_connection', response=list[ConnectionSchema])
def song_connection(request: HttpRequest, song_id: int):
	song = get_object_or_404(MediaSong.objects, id=song_id)
	return song.mediasongconnection_set


@tag_router.get('similar', response=list[TagWorkSchema])
def similar(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	tw = MediaWork.active_objects.filter(tags=tag).values_list('id', flat=True)
	return (
		TagWork.objects.exclude(id=tag.id)
		.filter(works__in=Subquery(tw), deprecated=False)
		.annotate(shared_works_count=Count('works', filter=Q(works__in=Subquery(tw))))
		.order_by('-shared_works_count')
		.filter(shared_works_count__gt=3)
	)[:10]


@tag_router.get(
	'query_connection', response={200: ConnectionLookupResponse, 404: Error}
)
def query_connection(request: HttpRequest, url: str):
	results = {}  # tag.pk -> (tag, has_connection)

	# TagWork connections
	twc_result = tag_work_connection_parser(url)
	if twc_result:
		site_type, content_id = twc_result
		for tag in TagWork.objects.filter(
			tagworkconnection__site=site_type,
			tagworkconnection__content_id=content_id,
			aliased_to__isnull=True,
		):
			results[tag.pk] = (tag, True)

	# Song connections -> work_tag
	sc_result = song_connection_parser(url)
	if sc_result:
		site_type, content_id = sc_result
		for song in MediaSong.objects.filter(
			mediasongconnection__site=site_type,
			mediasongconnection__content_id=content_id,
		):
			tag = song.work_tag
			if tag.pk not in results:
				results[tag.pk] = (tag, True)

	# Media connections -> tag
	mc_result = media_connection_parser(url)
	if mc_result:
		site_type, content_id = mc_result
		for tag in TagWork.objects.filter(
			tagworkmediaconnection__site=site_type,
			tagworkmediaconnection__content_id=content_id,
			aliased_to__isnull=True,
		):
			if tag.pk not in results:
				results[tag.pk] = (tag, True)

	# Creator/profile connections -> tag
	for conn_type, parser in profile_connection_parsers:
		content_id = parser(url)
		if content_id:
			for tag in TagWork.objects.filter(
				tagworkcreatorconnection__site=conn_type,
				tagworkcreatorconnection__content_id=content_id,
				aliased_to__isnull=True,
			):
				if tag.pk not in results:
					results[tag.pk] = (tag, True)
			break

	# Fallback: match tag names/aliases by last path segment of the URL
	last_segment = urlparse(url).path.rstrip('/').split('/')[-1]
	if last_segment:
		decoded_id = clean_incoming_tag_name(unquote(last_segment))
		if decoded_id:
			name_matched = TagWork.objects.filter(
				Q(name=decoded_id) | Q(aliases__name=decoded_id),
				aliased_to__isnull=True,
			).exclude(pk__in=results.keys())
			for tag in name_matched:
				results[tag.pk] = (tag, False)

	if not results:
		return 404, {'message': 'No matching entities found'}

	entities = []
	for tag, has_connection in results.values():
		tag.has_connection = has_connection
		entities.append(tag)

	return 200, {'entities': entities}
