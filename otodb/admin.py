from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from django import forms
from django.contrib import admin
from taggit.forms import TextareaTagWidget

from .models import (
    Category,
    Configuration,
    Implication,
    MediaSong,
    MediaWork,
    SourceWorkNiconico,
    SourceWorkYouTube,
    TaggedMedia,
    TagMain,
    WorkSource,
)


class MediaSourceInline(admin.TabularInline):
    model = WorkSource
    extra = 0


class TagMainAdmin(admin.ModelAdmin):
    readonly_fields = ('display_name',)
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }


class TaggedMediaAdmin(admin.ModelAdmin):
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }
    readonly_fields = [
        'tag',
    ]
    exclude = [
        'content_type',
        'object_id',
    ]


class MediaAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(MediaAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MediaWork
        widgets = {
            'tags': TextareaTagWidget
        }
        fields = '__all__'


class MediaSongInline(admin.TabularInline):
    model = MediaSong.media.through
    extra = 0


class MediaInline(admin.TabularInline):
    model = MediaSong.media.through
    extra = 0


class MediaAdmin(admin.ModelAdmin):
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.check_and_update_implications()

    form = MediaAdminForm
    inlines = [MediaSourceInline, MediaSongInline]
    list_display = [
        '__str__',
        'title',
    ]
    search_fields = [
        'title',
    ]


class MediaSongAdmin(admin.ModelAdmin):
    inlines = [MediaInline]


admin.site.register([
    Category,
    Implication,
    Configuration,
    SourceWorkNiconico,
    SourceWorkYouTube
])
admin.site.register(TagMain, TagMainAdmin)
admin.site.register(TaggedMedia, TaggedMediaAdmin)
admin.site.register(MediaWork, MediaAdmin)
admin.site.register(MediaSong, MediaSongAdmin)
