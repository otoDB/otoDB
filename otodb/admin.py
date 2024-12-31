from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from django import forms
from django.contrib import admin

from .models import (
    Configuration,
    Implication,
    MediaSong,
    MediaWork,
    Pool,
    TagWork,
    WorkSource,
)


class MediaSourceInline(admin.TabularInline):
    model = WorkSource
    extra = 0


class TagWorkAdmin(admin.ModelAdmin):
    readonly_fields = ('display_name',)
    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

class MediaAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(MediaAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MediaWork
        widgets = {
            # 'tags': TextareaTagWidget
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
    Implication,
    Configuration,
    Pool,
])
admin.site.register(TagWork, TagWorkAdmin)
admin.site.register(MediaWork, MediaAdmin)
admin.site.register(MediaSong, MediaSongAdmin)
