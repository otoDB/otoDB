from pydantic import field_validator, ValidationInfo
from ninja import Schema, ModelSchema, Field
from otodb.models import MediaWork, WorkSource, TagWork
from otodb.models.enums import WorkOrigin, WorkStatus, Platform, Rating

class Error(Schema):
    message: str

class TagSchema(ModelSchema):
    class Meta:
        model = TagWork
        fields = ['category', 'name', 'slug']

class WorkSourceSchema(ModelSchema):
    platform: str
    work_origin: str
    work_status: str
    class Meta:
        model = WorkSource
        fields = [
            'platform', 'url',
            'published_date',
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
    sources: list[WorkSourceSchema] = Field(..., alias='worksource_set')
    rating: str
    tags: list[TagSchema]
    class Meta:
        model = MediaWork
        fields = ['id', 'title', 'description', 'rating', 'thumbnail']

    @field_validator("rating", mode="before", check_fields=False)
    @classmethod
    def origin_str(cls, value) -> str:
        return Rating(value).label
