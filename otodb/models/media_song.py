from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagField

from .base import MediaBase
from .media_work import MediaWork
from .tag_main import TagWork

#  TODO whenever we get to songs...

class MediaSong(MediaBase):
    title = models.CharField(max_length=1000, null=False, blank=False)

    tags = TagField(
        to=TagWork,
        related_name="song_tags"
    )

    media = models.ManyToManyField(MediaWork, related_name='songs')

    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Song")
        verbose_name_plural = ("Songs")
