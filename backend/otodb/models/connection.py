from django.db import models
from simple_history.models import HistoricalRecords, HistoricForeignKey

from .media import MediaSong
from .tag import TagWork
from otodb.account.models import Account
from .enums import ProfileConnectionTypes, SongConnectionTypes, TagWorkConnectionTypes, MediaConnectionTypes

class ProfileConnection(models.Model):
    profile = models.ForeignKey(Account, on_delete=models.CASCADE)
    site = models.IntegerField(choices=ProfileConnectionTypes.choices)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("profile", "site", "content_id"),)

class MediaSongConnection(models.Model):
    song = HistoricForeignKey(MediaSong, on_delete=models.CASCADE)
    site = models.IntegerField(choices=SongConnectionTypes.choices)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("song", "site", "content_id"),)
    history = HistoricalRecords()

class TagWorkConnection(models.Model):
    tag = HistoricForeignKey(TagWork, on_delete=models.CASCADE)
    site = models.IntegerField(choices=TagWorkConnectionTypes.choices)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("tag", "site", "content_id"),)
    history = HistoricalRecords()

class TagWorkMediaConnection(models.Model):
    tag = HistoricForeignKey(TagWork, on_delete=models.CASCADE)
    site = models.IntegerField(choices=MediaConnectionTypes.choices)
    content_id = models.CharField(max_length=1000)
    class Meta:
        unique_together = (("tag", "site", "content_id"),)
    history = HistoricalRecords()

class TagWorkCreatorConnection(models.Model):
    tag = HistoricForeignKey(TagWork, on_delete=models.CASCADE)
    site = models.IntegerField(choices=ProfileConnectionTypes.choices)
    content_id = models.CharField(max_length=1000)
    dead = models.BooleanField(default=False, null=False)
    class Meta:
        unique_together = (("tag", "site", "content_id"),)
    history = HistoricalRecords()
