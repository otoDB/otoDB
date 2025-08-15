from typing import Annotated

from django.db import transaction
from django.db.models import Value
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, get_list_or_404

from pydantic import AfterValidator
from ninja import Router, ModelSchema, Schema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import NFKC
from otodb.models import TagWork, MediaWork, MediaSong, WikiPage, SongRelation, TagSong, TagWorkConnection, MediaSongConnection, TagWorkLangPreference, TagWorkMediaConnection, TagWorkCreatorConnection
from otodb.models.enums import WorkTagCategory, ProfileConnectionTypes, LanguageTypes

from .common import FatTagWorkSchema, TagWorkSchema, ThinWorkSchema, TagWorkDetailsSchema, user_is_trusted, RelationSchema, post_relation, SongSchema, TagSongSchema, ConnectionSchema

tag_router = Router()

@tag_router.get('search', response=list[TagWorkSchema])
@paginate
def search(request: HttpRequest, query: str, resolve_aliases: bool = True, category: int | None = None):
    qs = TagWork.objects.filter(name__icontains=NFKC(query).replace(' ', '_'), deprecated=False)
    if category is not None and category != -1:
        qs = qs.filter(category=category)
    
    if resolve_aliases:
        return list(set([t.aliased_to if t.aliased_to else t for t in qs]))
    else:
        return list(set(qs))

@tag_router.get('tag', response={ 200: FatTagWorkSchema, 300: str })
def tag(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    if tag.aliased_to:
        return 300, tag.aliased_to.slug
    return tag

@tag_router.get('details', response=TagWorkDetailsSchema)
def details(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    return {
        'tree': list(tag.get_tree())[:-1],
        'wiki_page': tag.wikipage_set,
        'aliases': tag.aliases
    }

@tag_router.get('works', response=list[ThinWorkSchema])
@paginate
def works(request: HttpRequest, tag_slug: str):
    return MediaWork.active_objects.filter(tags__slug=tag_slug)

@tag_router.post('alias', auth=django_auth)
@user_is_trusted
def alias_tags(request: HttpRequest, from_tags: list[str], into_tag: str, delete: bool):
    tags = []
    for slug in from_tags:
        try:
            tags.append(TagWork.objects.get(slug=slug))
        except TagWork.DoesNotExist:
            tags.append(TagWork.objects.create(name=slug))      
      
    into = get_object_or_404(TagWork, slug=into_tag)
    assert(into.aliased_to is None)

    TagWork.alias(tags, into)
    if delete:
        for tag in tags:
            tag.aliased_to = None
            tag.save()
            if tag.can_be_deleted:
                tag.delete()
    return

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

@tag_router.delete('lang_pref', auth=django_auth)
@user_is_trusted
def del_lang_pref(request: HttpRequest, tag_slug: str, lang: int):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    TagWorkLangPreference.objects.get(tag=tag, lang=LanguageTypes(lang).value).delete()

class TagInSchema(Schema):
    parent_slug: str | None
    category: int
    deprecated: bool

class SongInSchema(ModelSchema):
    class Meta:
        model = MediaSong
        fields = ['title', 'bpm', 'variable_bpm', 'author']

@tag_router.put('tag', auth=django_auth)
@user_is_trusted
@transaction.atomic
def update(request: HttpRequest, tag_slug: str, payload: TagInSchema, song_payload: SongInSchema | None = None):
    tag = get_object_or_404(TagWork.objects.select_related('mediasong').select_for_update(), slug=tag_slug)
    if tag.category == WorkTagCategory.SONG and payload.category != WorkTagCategory.SONG:
        tag.mediasong.delete()
    elif payload.category == WorkTagCategory.SONG:
        song_payload.title = song_payload.title.strip()
        song_payload.author = song_payload.author.strip()
        assert(song_payload.title)
        assert(song_payload.author)
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
    elif tag.category == WorkTagCategory.CREATOR and payload.category != WorkTagCategory.CREATOR:
        TagWorkCreatorConnection.objects.filter(tag=tag).delete()
    elif tag.category == WorkTagCategory.MEDIA and payload.category != WorkTagCategory.MEDIA:
        TagWorkMediaConnection.objects.filter(tag=tag).delete()

    tag.deprecated = payload.deprecated
    tag.category = payload.category
    if payload.parent_slug:
        parent = get_object_or_404(TagWork, slug=payload.parent_slug)
        assert(all(tag.id != t.id for t in parent.get_tree()))
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
    empty = md.strip() == ''
    try:
        wp = WikiPage.objects.get(tag=tag, lang=LanguageTypes(lang).value)
        if empty:
            wp.delete()
        else:
            wp.page = md
            wp.save() # Cannot use update_or_create here because the rendered page doesn't get rendered
    except WikiPage.DoesNotExist:
        if not empty:
            WikiPage.objects.create(tag=tag, lang=LanguageTypes(lang).value, page=md)

@tag_router.get('connection', response=tuple[list[ConnectionSchema], list[ConnectionSchema] | None])
def connection(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    cs = tag.tagworkconnection_set.all()
    if tag.category == WorkTagCategory.MEDIA:
        return 200, (cs, tag.tagworkmediaconnection_set.all())
    elif tag.category == WorkTagCategory.CREATOR:
        return 200, (cs, tag.tagworkcreatorconnection_set.all())
    return 200, (cs, None)

@tag_router.put('connection', auth=django_auth)
@user_is_trusted
def edit_connections(request: HttpRequest, tag_slug: str, payload: list[ConnectionSchema], t: int):
    Type = [
        TagWorkConnection,        # GENERAL
        None,                     # EVENT
        MediaSongConnection,      # SONG
        TagWorkMediaConnection,  # SOURCE
        TagWorkCreatorConnection, # CREATOR
        None                      # META
    ][t]
    assert(Type is not None)
    for connection in payload:
        connection.content_id = connection.content_id.strip()
        assert(connection.content_id != '')
        if Type is TagWorkCreatorConnection:
            assert(connection.site != ProfileConnectionTypes.WEBSITE) # Should be in general connection instead)
    tag = get_object_or_404(TagWork, slug=tag_slug)
    if t != WorkTagCategory.GENERAL:
        assert(t == tag.category)
    if Type is MediaSongConnection:
        song = tag.mediasong
        assert(song is not None)
        Type.objects.filter(song=song).delete()
        for connection in payload:
            MediaSongConnection.objects.create(song=song, site=connection.site,
                content_id=connection.content_id)
    else:
        Type.objects.filter(tag=tag).delete()
        for connection in payload:
            Type.objects.create(tag=tag, site=connection.site,
                content_id=connection.content_id)

@tag_router.get('song_search', response=list[SongSchema])
@paginate
def song_search(request: HttpRequest, query: str, tags: str | None = None):
    qs = MediaSong.objects.filter(title__icontains=query)
    if tags:
        for tag in tags.split():
            qs = qs.filter(tags__slug=NFKC(tag))
    elif query.isdigit():
        qs = qs.annotate(priority=Value(100))
        qs = MediaSong.objects.filter(id=int(query)).annotate(priority=Value(0)).union(qs)
        qs = qs.order_by('priority')
    return qs

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
    return TagSong.objects.filter(name__icontains=NFKC(query), aliased_to__isnull=True)

@tag_router.post('song_tags', auth=django_auth)
@user_is_trusted
def song_tags(request: HttpRequest, song_id: int, tags: list[Annotated[str, AfterValidator(NFKC)]]):
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
def update_song_tag(request: HttpRequest, tag_slug: str, payload: TagInSchema):
    tag = get_object_or_404(TagSong.objects.select_for_update(), slug=tag_slug)
    tag.category = payload.category
    if payload.parent_slug:
        parent = get_object_or_404(TagSong, slug=payload.parent_slug)
        assert(all(tag.id != t.id for t in parent.get_tree()))
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
