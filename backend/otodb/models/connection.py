from django.conf import settings
from django.db import models

from .enums import (
	MediaConnectionTypes,
	ProfileConnectionTypes,
	SongConnectionTypes,
	TagWorkConnectionTypes,
)
from .media import MediaSong
from .revision import RevisionTrackedModel
from .tag import TagWork


class ProfileConnection(models.Model):
	profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	site = models.IntegerField(choices=ProfileConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class Meta:
		unique_together = (('profile', 'site', 'content_id'),)


class MediaSongConnection(RevisionTrackedModel):
	song = models.ForeignKey(MediaSong, on_delete=models.CASCADE)
	site = models.IntegerField(choices=SongConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class RevisionMeta:
		tracked_fields = ['song', 'site', 'content_id']
		entity_attrs = ['song']

	class Meta:
		unique_together = (('song', 'site', 'content_id'),)


class TagWorkConnection(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
	site = models.IntegerField(choices=TagWorkConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class RevisionMeta:
		tracked_fields = ['tag', 'site', 'content_id']
		entity_attrs = ['tag']

	class Meta:
		unique_together = (('tag', 'site', 'content_id'),)


class TagWorkMediaConnection(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
	site = models.IntegerField(choices=MediaConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class RevisionMeta:
		tracked_fields = ['tag', 'site', 'content_id']
		entity_attrs = ['tag']

	class Meta:
		unique_together = (('tag', 'site', 'content_id'),)


class TagWorkCreatorConnection(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
	site = models.IntegerField(choices=ProfileConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)
	dead = models.BooleanField(default=False, null=False)

	class RevisionMeta:
		tracked_fields = ['tag', 'site', 'content_id', 'dead']
		entity_attrs = ['tag']

	class Meta:
		unique_together = (('tag', 'site', 'content_id'),)
