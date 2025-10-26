from django import forms
from django.contrib import admin
from django.db import models

from .models import (
	MediaSong,
	MediaWork,
	Pool,
	TagWork,
	TagSong,
	WorkSource,
	WorkSourceRejection,
	WorkRelation,
	SongRelation,
	TagWorkInstance,
	Post,
	PostContent,
)


class MediaSourceInline(admin.TabularInline):
	model = WorkSource
	extra = 0


class WorkRelationAInline(admin.TabularInline):
	model = WorkRelation
	fk_name = 'A'


class WorkRelationBInline(admin.TabularInline):
	model = WorkRelation
	fk_name = 'B'


class SongRelationAInline(admin.TabularInline):
	model = SongRelation
	fk_name = 'A'


class SongRelationBInline(admin.TabularInline):
	model = SongRelation
	fk_name = 'B'


class TagWorkInstanceInline(admin.TabularInline):
	model = TagWorkInstance
	show_change_link = True


class TagWorkAdmin(admin.ModelAdmin):
	readonly_fields = ('display_name',)
	search_fields = ['name', 'aliases__name']
	list_display = ['name', 'display_name', 'category', 'aliased_to']
	list_filter = ['category', 'aliased_to']


class TagWorkInstanceAdmin(admin.ModelAdmin):
	inlines = []


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
	inlines = [
		MediaSourceInline,
		WorkRelationAInline,
		WorkRelationBInline,
		TagWorkInstanceInline,
	]

	list_display = [
		'pk',
		'title',
		'rating',
		'sources_count',
		'tag_count',
		'creator_count',
		'source_count',
		'song_count',
		'general_count',
		'added_by',
	]
	search_fields = ['title']

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		return queryset.annotate(
			sources_count_annotation=models.Count('worksource', distinct=True),
			tag_count_annotation=models.Count('tags', distinct=True),
			creator_count_annotation=models.Count(
				'tags', filter=models.Q(tags__category=4), distinct=True
			),
			source_count_annotation=models.Count(
				'tags', filter=models.Q(tags__category=3), distinct=True
			),
			song_count_annotation=models.Count(
				'tags', filter=models.Q(tags__category=2), distinct=True
			),
			general_count_annotation=models.Count(
				'tags', filter=models.Q(tags__category=0), distinct=True
			),
			earliest_history_user=models.Subquery(
				queryset.model.history.filter(id=models.OuterRef('id'))
				.order_by('history_date')
				.values('history_user')[:1]
			),
		)

	@admin.display(description='Sources #', ordering='sources_count_annotation')
	def sources_count(self, obj):
		return obj.sources_count_annotation

	@admin.display(description='Total tags', ordering='tag_count_annotation')
	def tag_count(self, obj):
		return obj.tag_count_annotation

	@admin.display(description='Creator tag #', ordering='creator_count_annotation')
	def creator_count(self, obj):
		return obj.creator_count_annotation

	@admin.display(description='Source tag #', ordering='source_count_annotation')
	def source_count(self, obj):
		return obj.source_count_annotation

	@admin.display(description='Song tag #', ordering='song_count_annotation')
	def song_count(self, obj):
		return obj.song_count_annotation

	@admin.display(description='General tag #', ordering='general_count_annotation')
	def general_count(self, obj):
		return obj.general_count_annotation

	@admin.display(description='Added by', ordering='earliest_history_user')
	def added_by(self, obj):
		earliest_record = obj.history.order_by('history_date').first()
		if earliest_record and earliest_record.history_user:
			return earliest_record.history_user
		return '[Unknown]'


class MediaSongAdmin(MediaAdmin):
	inlines = [SongRelationAInline, SongRelationBInline]


class WorkSourceRejectionInline(admin.TabularInline):
	model = WorkSourceRejection


class WorkSourceAdmin(admin.ModelAdmin):
	list_display = ['__str__', 'title', 'platform', 'work_status', 'published_date']
	list_filter = ['work_status', 'platform', 'work_origin']
	search_fields = ['title', 'url', 'uploader_id']
	readonly_fields = ['info_payload']
	inlines = [WorkSourceRejectionInline]


class PostContentInline(admin.TabularInline):
	model = PostContent


class PostAdmin(admin.ModelAdmin):
	inlines = [PostContentInline]


admin.site.register(WorkSource, WorkSourceAdmin)
admin.site.register(Pool)
admin.site.register(TagWork, TagWorkAdmin)
admin.site.register(TagSong, TagWorkAdmin)
admin.site.register(MediaWork, MediaWorkAdmin)
admin.site.register(MediaSong, MediaSongAdmin)
admin.site.register(TagWorkInstance, TagWorkInstanceAdmin)
admin.site.register(Post, PostAdmin)
