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
    search_fields = ['name', 'aliases__name']
    list_display = ['name', 'display_name', 'category', 'parent', 'aliased_to']
    list_filter = ['category', 'aliased_to']

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

    list_display = ['pk', 'title', 'rating', 'sources_count', 'tag_count', 'creator_count', 'source_count', 'song_count', 'general_count', 'added_by']
    search_fields = ['title']

    @admin.display(description='Sources #')
    def sources_count(self, obj):
        return obj.worksource_set.count()

    @admin.display(description='Total tags')
    def tag_count(self, obj):
        return obj.tags.count()

    @admin.display(description='Creator tag #')
    def creator_count(self, obj):
        return obj.tags.filter(category=4).count()

    @admin.display(description='Source tag #')
    def source_count(self, obj):
        return obj.tags.filter(category=3).count()

    @admin.display(description='Song tag #')
    def song_count(self, obj):
        return obj.tags.filter(category=2).count()

    @admin.display(description='General tag #')
    def general_count(self, obj):
        return obj.tags.filter(category=0).count()

    @admin.display(description='Added by')
    def added_by(self, obj):
        earliest_record = obj.history.order_by('history_date').first()
        if earliest_record and earliest_record.history_user:
            return earliest_record.history_user
        return '[Unknown]'

class MediaSongAdmin(MediaAdmin):
    inlines = [SongRelationAInline, SongRelationBInline]

class WorkSourceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'title', 'platform', 'work_status', 'published_date']
    list_filter = ['work_status', 'platform', 'work_origin']
    search_fields = ['title', 'url', 'uploader_id']
    readonly_fields = ['info_payload']

admin.site.register(WorkSource, WorkSourceAdmin)
admin.site.register(Pool)
admin.site.register(TagWork, TagWorkAdmin)
admin.site.register(TagSong, TagWorkAdmin)
admin.site.register(MediaWork, MediaWorkAdmin)
admin.site.register(MediaSong, MediaSongAdmin)
admin.site.register(TagWorkInstance, TagWorkInstanceAdmin)
admin.site.register(Post)
