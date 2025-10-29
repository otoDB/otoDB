from typing import Annotated
from itertools import groupby
from functools import reduce
import re
from urllib.parse import urlparse, parse_qs

from django.db import transaction, models
from django.db.models import Value, F, Q, Case, When, Count
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, get_list_or_404

from pydantic import AfterValidator
from ninja import Router, ModelSchema, Schema, Query
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import clean_incoming_slug, clean_incoming_tag_name
from otodb.models import (
	TagWork,
	MediaWork,
	MediaSong,
	WikiPage,
	SongRelation,
	TagSong,
	TagWorkConnection,
	MediaSongConnection,
	TagWorkLangPreference,
	TagWorkMediaConnection,
	TagWorkCreatorConnection,
	TagWorkParenthood,
)
from otodb.models.enums import (
	WorkTagCategory,
	LanguageTypes,
	SongConnectionTypes,
	TagWorkConnectionTypes,
	MediaConnectionTypes,
)

from .common import (
	FatTagWorkSchema,
	TagWorkSchema,
	ThinWorkSchema,
	TagWorkDetailsSchema,
	user_is_trusted,
	RelationSchema,
	post_relation,
	SongSchema,
	TagSongSchema,
	ConnectionSchema,
	profile_connection_parsers,
	make_alt_value_parser,
	re_to_parser,
)

tag_router = Router()


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
):
	qs = TagWork.objects.filter(name__contains=clean_incoming_tag_name(query))

	if resolve_aliases:
		qs = qs.filter(aliased_to__isnull=True) | TagWork.objects.filter(
			id__in=qs.values('aliased_to__id')
		)

	if category is not None and category != -1:
		qs = qs.filter(category=category)
		if category == WorkTagCategory.MEDIA and media_type:
			qs = filter_tags_by_media_type(qs, media_type)

	return (
		qs.filter(deprecated=False)
		.annotate(
			n_instance=Case(
				When(
					aliased_to__isnull=False, then=Count('aliased_to__tagworkinstance')
				),
				default=Count('tagworkinstance'),
				output_field=models.IntegerField(),
			)
		)
		.order_by('-n_instance')
	)


@tag_router.get('tag', response={200: FatTagWorkSchema, 300: str})
def tag(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	if tag.aliased_to:
		return 300, tag.aliased_to.slug
	return tag


@tag_router.get('details', response=TagWorkDetailsSchema)
def details(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(
		TagWork.objects.prefetch_related('childhood', 'wikipage_set'), slug=tag_slug
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
	return MediaWork.active_objects.filter(tags__slug=tag_slug).select_related(
		'thumbnail_source'
	)


@tag_router.post('alias', auth=django_auth)
@user_is_trusted
def alias_tags(request: HttpRequest, from_tags: list[str], into_tag: str, delete: bool):
	tags = []
	for tag_name in from_tags:
		try:
			tags.append(TagWork.objects.get(slug=clean_incoming_slug(tag_name)))
		except TagWork.DoesNotExist:
			tags.append(TagWork.objects.create(name=tag_name))

	into = get_object_or_404(TagWork.objects.select_related('aliased_to'), slug=clean_incoming_slug(into_tag))
	if into.aliased_to:
		into = into.aliased_to
	assert into.aliased_to is None

	TagWork.alias(tags, into)
	if delete:
		for tag in tags:
			tag.aliased_to = None
			tag.save()
			if tag.can_be_deleted:
				tag.delete()

	return {'merged_slug': into.slug}


@tag_router.delete('tag', auth=django_auth, response={200: None, 400: None})
@user_is_trusted
def delete(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	if tag.can_be_deleted:
		tag.delete()
	else:
		return 400, None


@tag_router.delete('alias', auth=django_auth)
@user_is_trusted
def remove_alias(request: HttpRequest, tag_slug: str, alias: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	tag.aliases.filter(slug=alias).update(aliased_to=None)


@tag_router.put('lang_pref', auth=django_auth)
@user_is_trusted
def add_lang_pref(request: HttpRequest, tag_slug: str, lang: int):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	tag.lang_prefs.filter(lang=LanguageTypes(lang).value).delete()
	TagWorkLangPreference.objects.create(tag=tag, lang=lang)


@tag_router.post('set_base', auth=django_auth)
@user_is_trusted
def set_base_tag(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	to = tag.aliased_to
	assert to is not None

	to.tagworkinstance_set.update(work_tag=tag)
	TagWork.transfer_data(to, tag)

	to.aliases.update(aliased_to_id=tag.id)
	to.aliased_to = tag
	to.save()
	tag.aliased_to = None
	tag.save()


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
	if (
		tag.category == WorkTagCategory.CREATOR
		and payload.category != WorkTagCategory.CREATOR
	):
		TagWorkCreatorConnection.objects.filter(tag=tag).delete()
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
def edit_wiki_page(request: HttpRequest, tag_slug: str, lang: int, md: str):
	tag = get_object_or_404(TagWork, slug=tag_slug)
	empty = md.strip() == ''
	try:
		wp = WikiPage.objects.get(tag=tag, lang=LanguageTypes(lang).value)
		if empty:
			wp.delete()
		else:
			wp.page = md
			wp.save()  # Cannot use update_or_create here because the rendered page doesn't get rendered
	except WikiPage.DoesNotExist:
		if not empty:
			WikiPage.objects.create(tag=tag, lang=LanguageTypes(lang).value, page=md)


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
		re_to_parser(re.compile(r'https?:\/\/dic\.nicovideo\.jp\/a\/([^/?#]+)\/?')),
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
	qs = MediaSong.objects.filter(title__icontains=query, author__icontains=author)
	if tags:
		for tag in tags.split():
			qs = qs.filter(tags__slug=clean_incoming_slug(tag))
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
@user_is_trusted
def song_relation(request: HttpRequest, payload: RelationSchema):
	post_relation(MediaSong, payload)
	return


@tag_router.delete('song_relation', auth=django_auth)
@user_is_trusted
def delete_relation(request: HttpRequest, A: int, B: int):
	a = MediaSong.active_objects.get(id=A)
	b = MediaSong.active_objects.get(id=B)
	rel = SongRelation.objects.get(a, b)
	rel.delete()
	return


@tag_router.get('song_tag_search', response=list[TagSongSchema])
@paginate
def song_tag_search(request: HttpRequest, query: str):
	return TagSong.objects.filter(
		name__contains=clean_incoming_tag_name(query), aliased_to__isnull=True
	)


@tag_router.post('song_tags', auth=django_auth)
@user_is_trusted
def song_tags(
	request: HttpRequest,
	song_id: int,
	tags: list[Annotated[str, AfterValidator(clean_incoming_tag_name)]],
):
	song = get_object_or_404(MediaSong.objects, id=song_id)
	song.tags.set(tags)
	return


@tag_router.get('song_tag', response=TagSongSchema)
def song_tag(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagSong, slug=tag_slug, aliased_to__isnull=True)
	return tag


@tag_router.get('song_tag_details', response=list[str])
def song_tag_details(request: HttpRequest, tag_slug: str):
	tag = get_object_or_404(TagSong, slug=tag_slug)
	return list(tag.get_tree())[:-1]


@tag_router.put('song_tag', auth=django_auth)
@user_is_trusted
@transaction.atomic
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
