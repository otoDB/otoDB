from django.contrib import admin
from .models import (
    Category, Implication, Media, TagMain, Configuration, TaggedMedia
)

admin.site.register([
    Category,
    Implication,
    Media,
    TagMain,
    TaggedMedia,
    Configuration
])
