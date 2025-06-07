from django.db import models

from .media import MediaSong
from .tag import TagWork
from otodb.account.models import Account
from .enums import ProfileConnectionTypes, SongConnectionTypes, TagWorkConnectionTypes, SourceConnectionTypes

class ProfileConnection(models.Model):
    profile = models.ForeignKey(Account, on_delete=models.CASCADE)
    site = models.IntegerField(choices=ProfileConnectionTypes)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("profile", "site", "content_id"),)

class MediaSongConnection(models.Model):
    song = models.ForeignKey(MediaSong, on_delete=models.CASCADE)
    site = models.IntegerField(choices=SongConnectionTypes)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("song", "site", "content_id"),)

class TagWorkConnection(models.Model):
    tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
    site = models.IntegerField(choices=TagWorkConnectionTypes)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("tag", "site", "content_id"),)

class TagWorkSourceConnection(models.Model):
    tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
    site = models.IntegerField(choices=SourceConnectionTypes)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("tag", "site", "content_id"),)

class TagWorkCreatorConnection(models.Model):
    tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)
    site = models.IntegerField(choices=ProfileConnectionTypes)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("tag", "site", "content_id"),)
