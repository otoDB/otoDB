from typing import Optional

from pydantic import field_validator, ValidationInfo

from ninja import Schema, ModelSchema, Field

from otodb.account.models import Account
from otodb.models import MediaWork, WorkSource, TagWork, Pool, PoolItem, MediaSong
from otodb.models.enums import WorkOrigin, WorkStatus, Platform, Rating, WorkTagCategory

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
    category: str
    children: list['TagWorkSchema']
    song: Optional[SongSchema] = Field(None, alias='get_song')
    class Meta:
        model = TagWork
        fields = ['name', 'slug']

    @field_validator("aliases", mode="before", check_fields=False)
    @classmethod
    def platform_str(cls, value) -> str:
        return [tag.name for tag in value]
        
    @field_validator("category", mode="before", check_fields=False)
    @classmethod
    def category_str(cls, value) -> str:
        return WorkTagCategory(value).label

class TagWorkDetailsSchema(Schema):
    tree: list[TagWorkSchema]
    wiki_page: Optional[str]

class WorkSourceSchema(ModelSchema):
    platform: str
    work_origin: str
    work_status: str
    class Meta:
        model = WorkSource
        fields = [
            'platform', 'url',
            'published_date', 'id',
            'work_width', 'work_height',
            'title', 'description'
        ]

    @field_validator("platform", "work_status", "work_origin", mode="before", check_fields=False)
    @classmethod
    def platform_str(cls, value, info: ValidationInfo) -> str:
        match info.field_name:
            case "platform":
                return Platform(value).label
            case "work_status":
                return WorkStatus(value).label
            case "work_origin":
                return WorkOrigin(value).label

class WorkSchema(ModelSchema):
    rating: str
    tags: list[TagWorkSchema]
    class Meta:
        model = MediaWork
        fields = ['id', 'title', 'description', 'rating', 'thumbnail']

    @field_validator("rating", mode="before", check_fields=False)
    @classmethod
    def origin_str(cls, value) -> str:
        return Rating(value).label

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
