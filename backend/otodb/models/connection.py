from django.db import models

from .media import MediaSong
from .tag import TagWork
from otodb.account.models import Account
from .enums import (
	ProfileConnectionTypes,
	SongConnectionTypes,
	TagWorkConnectionTypes,
	MediaConnectionTypes,
)
from .revision import RevisionTrackedModel


class ProfileConnection(models.Model):
	profile = models.ForeignKey(Account, on_delete=models.CASCADE)
	site = models.IntegerField(choices=ProfileConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class Meta:
		unique_together = (('profile', 'site', 'content_id'),)


class MediaSongConnection(RevisionTrackedModel):
	song = models.ForeignKey(MediaSong, on_delete=models.CASCADE)
	site = models.IntegerField(choices=SongConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class Meta:
		unique_together = (('song', 'site', 'content_id'),)

	revision_tracked_fields = ['tag', 'site', 'content_id']


class TagWorkConnection(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
	site = models.IntegerField(choices=TagWorkConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class Meta:
		unique_together = (('tag', 'site', 'content_id'),)

	revision_tracked_fields = ['tag', 'site', 'content_id']


class TagWorkMediaConnection(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
	site = models.IntegerField(choices=MediaConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)

	class Meta:
		unique_together = (('tag', 'site', 'content_id'),)

	revision_tracked_fields = ['tag', 'site', 'content_id']


class TagWorkCreatorConnection(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
	site = models.IntegerField(choices=ProfileConnectionTypes.choices)
	content_id = models.CharField(max_length=1000)
	dead = models.BooleanField(default=False, null=False)

	class Meta:
		unique_together = (('tag', 'site', 'content_id'),)

	revision_tracked_fields = ['tag', 'site', 'content_id', 'dead']
