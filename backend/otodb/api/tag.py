from typing import Optional

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja.pagination import paginate

from otodb.models import TagWork, MediaWork

from .common import TagWorkSchema, WorkSchema, TagWorkDetailsSchema

tag_router = Router()

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
    return MediaWork.objects.filter(tags__slug=tag_slug, moved_to__isnull=True)
