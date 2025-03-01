from django.http import HttpRequest
from django.shortcuts import get_object_or_404, get_list_or_404

from ninja import Router, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.models import TagWork, MediaWork

from .common import TagWorkSchema, WorkSchema, TagWorkDetailsSchema

tag_router = Router()

@tag_router.get('search', response=list[TagWorkSchema])
def search(request: HttpRequest, query: str):
    return TagWork.objects.filter(name__icontains=query, aliased_to__isnull=True)

@tag_router.get('tag', response=TagWorkSchema)
def tag(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    return tag

@tag_router.get('details', response=TagWorkDetailsSchema)
def details(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    return {
        'tree': list(tag.get_tree())[:-1],
        'wiki_page': tag.wiki_page and tag.wiki_page.page_rendered
    }

@tag_router.get('works', response=list[WorkSchema])
@paginate
def works(request: HttpRequest, tag_slug: str):
    return MediaWork.active_objects.filter(tags__slug=tag_slug)

@tag_router.post('alias', auth=django_auth)
def alias_tags(request: HttpRequest, from_tags: list[str], into_tag: str):
    tags = get_list_or_404(slug__in=from_tags)
    into = get_object_or_404(slug=into_tag)
    assert(into.aliased_to is None)
    
    TagWork.alias(tags, into)
    return

class TagInSchema(ModelSchema):
    parent_slug: str | None
    class Meta:
        model = TagWork
        fields = ['category']

@tag_router.put('tag', auth=django_auth)
def update(request, tag_slug: str, payload: TagInSchema):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    tag.category = payload.category
    if payload.parent_slug:
        assert(tag.parent_slug != tag.slug)
        tag.parent = get_object_or_404(TagWork, slug=payload.parent_slug)
    else:
        tag.parent = None
    tag.save()
    return
