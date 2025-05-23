from typing import Optional
from functools import wraps

from pydantic import field_validator

from ninja import Schema, ModelSchema, Field

from otodb.account.models import Account
from otodb.models import MediaWork, WorkSource, TagWork, TagSong, Pool, PoolItem, MediaSong, WorkRelation, SongRelation

class Error(Schema):
    message: str

class ProfileSchema(ModelSchema):
    id: int
    class Meta:
        model = Account
        fields = ['username', 'level', 'date_created']

class TagSongSchema(ModelSchema):
    id: int
    aliases: list[str]
    children: list['TagSongSchema']
    class Meta:
        model = TagSong
        fields = ['name', 'slug', 'category']

    @field_validator("aliases", mode="before", check_fields=False)
    @classmethod
    def aliases_str(cls, value) -> str:
        return [tag.name for tag in value]

class SongSchema(ModelSchema):
    id: int
    work_tag: str
    tags: list[TagSongSchema]
    class Meta:
        model = MediaSong
        fields = ['title', 'bpm', 'author', 'tags']

    @field_validator("work_tag", mode="before", check_fields=False)
    @classmethod
    def tag_slug(cls, value) -> str:
        return value.slug

class TagWorkSchema(ModelSchema):
    id: int
    aliases: list[str]
    children: list['TagWorkSchema']
    song: Optional[SongSchema] = Field(None, alias='get_song')
    class Meta:
        model = TagWork
        fields = ['name', 'slug', 'category']

    @field_validator("aliases", mode="before", check_fields=False)
    @classmethod
    def aliases_str(cls, value) -> str:
        return [tag.slug for tag in value]

class TagWorkDetailsSchema(Schema):
    tree: list[TagWorkSchema]
    wiki_page: Optional[str]

class WorkSourceSchema(ModelSchema):
    id: int
    added_by: ProfileSchema
    class Meta:
        model = WorkSource
        fields = [
            'platform', 'url',
            'published_date',
            'work_width', 'work_height',
            'title', 'description',
            'work_origin', 'work_status',
            'thumbnail', 'rejection_reason',
            'source_id'
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
    pending_items: list[WorkSourceSchema]
    class Meta:
        model = Pool
        fields = ['name', 'description']

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
user_is_moderator = perm_decorator_ctor(lambda user: user.is_moderator)
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
