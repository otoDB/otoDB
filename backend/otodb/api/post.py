from datetime import datetime

from django.db.models import Subquery, OuterRef
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router, ModelSchema
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import Post, PostContent
from otodb.models.enums import PostCategory, LanguageTypes

from .common import ProfileSchema, user_is_trusted

post_router = Router()

class PostContentSchema(ModelSchema):
    class Meta:
        model = PostContent
        fields = ['lang', 'page_rendered', 'modified']

class PostSchema(ModelSchema):
    added_by: ProfileSchema
    pages: list[PostContentSchema]
    class Meta:
        model = Post
        fields = ['title', 'category']

class PostOverviewSchema(ModelSchema):
    id: int
    added_by: ProfileSchema
    modified: datetime
    class Meta:
        model = Post
        fields = ['title', 'category']

@post_router.get('post', response=PostSchema)
def post(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return post

def annotate_modified(qs):
    return qs.annotate(
        modified=Subquery(PostContent.objects.filter(post_id=OuterRef('id')).order_by('modified').values('modified')[:1])
    )

@post_router.get('categories', response=list[list[PostOverviewSchema]])
def categories(request: HttpRequest):
    return [annotate_modified(Post.objects.filter(category=i)).order_by('-modified')[:5] for i, _ in PostCategory.choices]

@post_router.get('category', response=list[PostOverviewSchema])
@paginate
def category(request: HttpRequest, category: PostCategory):
    return annotate_modified(Post.objects.filter(category=category)).order_by('-modified')

@post_router.post('post', response=int, auth=django_auth)
@user_is_trusted
def new(request: HttpRequest, title: str, post: str, category: PostCategory, lang: LanguageTypes):
    assert(category > 0)
    assert(title)
    assert(post)
    p = Post.objects.create(title=title, added_by=request.user, category=category)
    PostContent.objects.create(post=p, lang=lang, page=post)
    return p.id

@post_router.get('search', response=list[PostOverviewSchema])
@paginate
def search(request: HttpRequest, query: str, category: PostCategory | None = None):
    posts = annotate_modified(Post.objects.filter(title__icontains=query))
    if category is not None and category >= 0:
        posts = posts.filter(category=category)
    return posts
