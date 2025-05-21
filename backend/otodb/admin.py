from django import forms
from django.contrib import admin

from .models import (
    MediaSong,
    MediaWork,
    Pool,
    TagWork,
    TagSong,
    WorkSource,
    WorkRelation,
    SongRelation,
    TagWorkInstance,
    TagWorkVote,
    Post,
)

class MediaSourceInline(admin.TabularInline):
    model = WorkSource
    extra = 0

class WorkRelationAInline(admin.TabularInline):
    model = WorkRelation
    fk_name = "A"

class WorkRelationBInline(admin.TabularInline):
    model = WorkRelation
    fk_name = "B"

class SongRelationAInline(admin.TabularInline):
    model = SongRelation
    fk_name = "A"

class SongRelationBInline(admin.TabularInline):
    model = SongRelation
    fk_name = "B"

class TagWorkInstanceInline(admin.TabularInline):
    model = TagWorkInstance
    show_change_link = True

class TagWorkAdmin(admin.ModelAdmin):
    readonly_fields = ('display_name',)

class TagWorkVoteInline(admin.TabularInline):
    model = TagWorkVote

class TagWorkInstanceAdmin(admin.ModelAdmin):
    inlines = [TagWorkVoteInline]

class MediaAdminForm(forms.ModelForm):
    class Meta:
        model = MediaWork
        fields = '__all__'

class MediaAdmin(admin.ModelAdmin):
    form = MediaAdminForm

    list_display = [
        '__str__',
        'title',
    ]
    search_fields = [
        'title',
    ]

class MediaWorkAdmin(MediaAdmin):
    inlines = [MediaSourceInline, WorkRelationAInline, WorkRelationBInline, TagWorkInstanceInline]

class MediaSongAdmin(MediaAdmin):
    inlines = [SongRelationAInline, SongRelationBInline]

admin.site.register([
    Pool, WorkSource
])
admin.site.register(TagWork, TagWorkAdmin)
admin.site.register(TagSong, TagWorkAdmin)
admin.site.register(MediaWork, MediaWorkAdmin)
admin.site.register(MediaSong, MediaSongAdmin)
admin.site.register(TagWorkInstance, TagWorkInstanceAdmin)
admin.site.register(Post)
