from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router
from ninja import ModelSchema

from otodb.models import Post, PostContent

from .common import ProfileSchema

post_router = Router()

class PostContentSchema(ModelSchema):
    class Meta:
        model = PostContent
        fields = ['lang', 'page_rendered']

class PostSchema(ModelSchema):
    added_by: ProfileSchema
    pages: list[PostContentSchema]
    class Meta:
        model = Post
        fields = ['title']

@post_router.get('post', response=PostSchema)
def post(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    return post
