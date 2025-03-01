from typing import Optional

from pydantic import field_validator

from ninja import Schema, ModelSchema, Field

from otodb.account.models import Account
from otodb.models import MediaWork, WorkSource, TagWork, Pool, PoolItem, MediaSong

class Error(Schema):
    message: str

class ProfileSchema(ModelSchema):
    class Meta:
        model = Account
        fields = ['username', 'email', 'level', 'date_created']

class SongSchema(ModelSchema):
    class Meta:
        model = MediaSong
        fields = ['title', 'bpm', 'author']

class TagWorkSchema(ModelSchema):
    aliases: list[str]
    children: list['TagWorkSchema']
    song: Optional[SongSchema] = Field(None, alias='get_song')
    class Meta:
        model = TagWork
        fields = ['name', 'slug', 'category']

    @field_validator("aliases", mode="before", check_fields=False)
    @classmethod
    def aliases_str(cls, value) -> str:
        return [tag.name for tag in value]

class TagWorkDetailsSchema(Schema):
    tree: list[TagWorkSchema]
    wiki_page: Optional[str]

class WorkSourceSchema(ModelSchema):
    class Meta:
        model = WorkSource
        fields = [
            'platform', 'url',
            'published_date', 'id',
            'work_width', 'work_height',
            'title', 'description',
            'work_origin', 'work_status'
        ]

class WorkSchema(ModelSchema):
    tags: list[TagWorkSchema]
    class Meta:
        model = MediaWork
        fields = ['id', 'title', 'description', 'rating', 'thumbnail', 'rating']

class ListItemSchema(ModelSchema):
    work: WorkSchema
    class Meta:
        model = PoolItem
        fields = ['description']

class ListSchema(ModelSchema):
    author: ProfileSchema
    class Meta:
        model = Pool
        fields = ['name', 'description', 'id']
