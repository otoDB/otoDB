from typing import Optional, Annotated
from functools import wraps

from pydantic import field_validator

from ninja import Schema, ModelSchema, Field, Query

from otodb.account.models import Account
from otodb.models import (
    MediaWork, WorkSource, MediaSong, WorkSourceRejection,
    TagWork, TagSong, TagWorkLangPreference, WikiPage,
    Pool, PoolItem,
    WorkRelation, SongRelation
)

class Error(Schema):
    message: str

class ProfileSchema(ModelSchema):
    id: int
    class Meta:
        model = Account
        fields = ['username', 'level', 'date_created']

class TagWorkLangPreferenceSchema(ModelSchema):
    tag: str
    class Meta:
        model = TagWorkLangPreference
        fields = ['lang']

    @field_validator("tag", mode="before", check_fields=False)
    @classmethod
    def tag_slug(cls, value) -> str:
        return value.name

class TagSongSchema(ModelSchema):
    id: int
    children: list['TagSongSchema']
    class Meta:
        model = TagSong
        fields = ['name', 'slug', 'category']

class SongSchema(ModelSchema):
    id: int
    work_tag: str
    tags: list[TagSongSchema]
    class Meta:
        model = MediaSong
        fields = ['title', 'bpm', 'variable_bpm', 'author', 'tags']

    @field_validator("work_tag", mode="before", check_fields=False)
    @classmethod
    def tag_slug(cls, value) -> str:
        return value.slug

class TagWorkSchema(ModelSchema):
    id: int
    children: list['TagWorkSchema']
    song: Optional[SongSchema] = Field(None, alias='get_song')
    lang_prefs: list[TagWorkLangPreferenceSchema]
    class Meta:
        model = TagWork
        fields = ['name', 'slug', 'category']

class WikiPageSchema(ModelSchema):
    class Meta:
        model = WikiPage
        fields = ['page_rendered', 'lang']

class TagWorkDetailsSchema(Schema):
    tree: list[TagWorkSchema]
    wiki_page: list[WikiPageSchema]
    aliases: list[TagWorkSchema]

class WorkSourceRejectionSchema(ModelSchema):
    by: ProfileSchema
    class Meta:
        model = WorkSourceRejection
        fields = ['reason']

class WorkSourceSchema(ModelSchema):
    id: int
    added_by: ProfileSchema
    rejection: WorkSourceRejectionSchema | None = None
    class Meta:
        model = WorkSource
        fields = [
            'platform', 'url',
            'published_date',
            'work_width', 'work_height', 'work_duration',
            'title', 'description',
            'work_origin', 'work_status',
            'thumbnail', 'source_id'
        ]

class WorkSchema(ModelSchema):
    id: int
    tags: list[TagWorkSchema]
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'rating', 'thumbnail', 'rating']

class ListItemSchema(ModelSchema):
    work: WorkSchema
    class Meta:
        model = PoolItem
        fields = ['description']

class ListSchema(ModelSchema):
    id: int
    author: ProfileSchema
    upstream: str | None = Field(None, alias="poolupstream")
    class Meta:
        model = Pool
        fields = ['name', 'description']

    @field_validator("upstream", mode="before", check_fields=False)
    @classmethod
    def upstream_str(cls, value) -> str:
        return value.upstream

def perm_decorator_ctor(uf):
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if uf(request.user):
                return f(request, *args, **kwargs)
            else:
                return 403
        return wrapper
    return decorator

user_is_trusted = perm_decorator_ctor(lambda user: user.level > Account.Levels.RESTRICTED)
user_is_editor = perm_decorator_ctor(lambda user: user.is_editor)
user_is_staff = perm_decorator_ctor(lambda user: user.is_staff)

class RelationSchema(Schema):
    A_id: int
    B_id: int
    relation: int

def post_relation(cls, payload: RelationSchema):
    assert(cls is MediaWork or cls is MediaSong)
    manager = cls.active_objects if cls is MediaWork else cls.objects
    rel_cls = WorkRelation if cls is MediaWork else SongRelation
    A = manager.get(id=payload.A_id)
    B = manager.get(id=payload.B_id)
    try:
        rel = rel_cls.objects.get(A, B)
        rel.A = A
        rel.B = B
        rel.relation = payload.relation
        rel.save()
    except rel_cls.DoesNotExist:
        rel = rel_cls.objects.create(A=A, B=B, relation=payload.relation)
    return

class ConnectionSchema(Schema):
    site: int
    content_id: Annotated[str, Query(min_length=1)]
