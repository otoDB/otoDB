import unicodedata

from django.http import HttpRequest
from django.shortcuts import get_object_or_404, get_list_or_404

from ninja import Router, ModelSchema, Schema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.models import TagWork, MediaWork, MediaSong, WikiPage, SongRelation, TagSong, TagWorkConnection, MediaSongConnection, TagWorkLangPreference
from otodb.models.enums import WorkTagCategory

from .common import TagWorkSchema, WorkSchema, TagWorkDetailsSchema, user_is_trusted, RelationSchema, post_relation, SongSchema, TagSongSchema, ConnectionSchema, WikiPageSchema

tag_router = Router()

@tag_router.get('search', response=list[TagWorkSchema])
@paginate
def search(request: HttpRequest, query: str, category: int | None = None):
    qs = TagWork.objects.filter(name__icontains=unicodedata.normalize('NFKD', query), aliased_to__isnull=True)
    if category is not None and category != -1:
        qs = qs.filter(category=category)
    return qs

@tag_router.get('tag', response=TagWorkSchema)
def tag(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug, aliased_to__isnull=True)
    return tag

@tag_router.get('details', response=TagWorkDetailsSchema)
def details(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    return {
        'tree': list(tag.get_tree())[:-1],
        'wiki_page': tag.wikipage_set,
        'aliases': tag.aliases
    }

@tag_router.get('works', response=list[WorkSchema])
@paginate
def works(request: HttpRequest, tag_slug: str):
    return MediaWork.active_objects.filter(tags__slug=tag_slug)

@tag_router.post('alias', auth=django_auth)
@user_is_trusted
def alias_tags(request: HttpRequest, from_tags: list[str], into_tag: str):
    tags = get_list_or_404(TagWork, slug__in=from_tags)
    into = get_object_or_404(TagWork, slug=into_tag)
    assert(into.aliased_to is None)
    
    TagWork.alias(tags, into)
    return

@tag_router.delete('alias', auth=django_auth)
@user_is_trusted
def remove_alias(request: HttpRequest, tag_slug: str, alias: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    tag.aliases.filter(name=alias).update(aliased_to=None)

@tag_router.put('lang_pref', auth=django_auth)
@user_is_trusted
def add_lang_pref(request: HttpRequest, tag_slug: str, lang: int):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    tag.lang_prefs.filter(lang=lang).delete()
    TagWorkLangPreference.objects.create(tag=tag, lang=lang)

@tag_router.delete('lang_pref', auth=django_auth)
@user_is_trusted
def del_lang_pref(request: HttpRequest, tag_slug: str, lang: int):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    TagWorkLangPreference.objects.get(tag=tag, lang=lang).delete()

class TagInSchema(Schema):
    parent_slug: str | None
    category: int

@tag_router.put('tag', auth=django_auth)
@user_is_trusted
def update(request: HttpRequest, tag_slug: str, payload: TagInSchema):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    if tag.category == WorkTagCategory.SONG and payload.category != WorkTagCategory.SONG:
        tag.mediasong.delete()
    tag.category = payload.category
    if payload.parent_slug:
        parent = get_object_or_404(TagWork, slug=payload.parent_slug)
        assert(tag.id != t.id for t in parent.get_tree())
        tag.parent = parent
    else:
        tag.parent = None
    tag.save()
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
    WikiPage.objects.update_or_create(tag=tag, lang=lang, defaults={'page':md})

@tag_router.get('connection', response=list[ConnectionSchema])
def connection(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    return tag.tagworkconnection_set

@tag_router.put('connection', auth=django_auth)
@user_is_trusted
def edit_connection(request: HttpRequest, tag_slug: str, payload: ConnectionSchema):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    TagWorkConnection.objects.update_or_create(tag=tag, site=payload.site,
        defaults={ 'content_id': payload.content_id })

@tag_router.delete('connection', auth=django_auth)
@user_is_trusted
def delete_connection(request: HttpRequest, tag_slug: str, site: int):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    TagWorkConnection.objects.get(tag=tag, site=site).delete()

@tag_router.get('song_search', response=list[SongSchema])
@paginate
def song_search(request: HttpRequest, query: str):
    return MediaSong.objects.filter(title__icontains=query)

class SongInSchema(ModelSchema):
    class Meta:
        model = MediaSong
        fields = ['title', 'bpm', 'author']

@tag_router.post('song', auth=django_auth)
@user_is_trusted
def song(request: HttpRequest, tag_slug: str, payload: SongInSchema):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    try:
        song = tag.mediasong
        song.title = payload.title
        song.bpm = payload.bpm
        song.author = payload.author
        song.save()
    except MediaSong.DoesNotExist:
        tag.category = WorkTagCategory.SONG
        tag.save()
        song = MediaSong.objects.create(work_tag=tag, **payload.dict())
    return

@tag_router.get('song_relations', response=tuple[list[RelationSchema], list[SongSchema]])
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
    return TagSong.objects.filter(name__icontains=unicodedata.normalize('NFKD', query), aliased_to__isnull=True)

@tag_router.post('song_tags', auth=django_auth)
@user_is_trusted
def song_tags(request: HttpRequest, song_id: int, tags: list[str]):
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
def update_song_tag(request: HttpRequest, tag_slug: str, payload: TagInSchema):
    tag = get_object_or_404(TagSong, slug=tag_slug)
    tag.category = payload.category
    if payload.parent_slug:
        parent = get_object_or_404(TagSong, slug=payload.parent_slug)
        assert(tag.id != t.id for t in parent.get_tree())
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

@tag_router.put('song_connection', auth=django_auth)
@user_is_trusted
def edit_song_connection(request: HttpRequest, song_id: int, payload: ConnectionSchema):
    song = get_object_or_404(MediaSong.objects, id=song_id)
    MediaSongConnection.objects.update_or_create(song=song, site=payload.site,
        defaults={ 'content_id': payload.content_id })

@tag_router.delete('song_connection', auth=django_auth)
@user_is_trusted
def delete_song_connection(request: HttpRequest, song_id: int, site: int):
    song = get_object_or_404(MediaSong.objects, id=song_id)
    MediaSongConnection.objects.get(song=song, site=site).delete()
