from django.db import models
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from .base import MediaBase
from .media_work import MediaWork
from .tagged_media import TaggedMedia


class MediaSong(MediaBase):
    title = models.CharField(max_length=1000, null=False, blank=False)
    title_translated = models.CharField(max_length=1000, null=True, blank=True)

    tags = TaggableManager(
        through=TaggedMedia,
        related_name="song_tags",
        help_text="A space-separated list of tags."
    )

    media = models.ManyToManyField(MediaWork, related_name='songs')

    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Song")
        verbose_name_plural = ("Songs")
