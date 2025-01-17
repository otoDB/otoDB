from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagField

from .base import MediaBaseManager
from .tag import TagWork, TagSong

class MediaSong(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    bpm = models.FloatField(null=False)
    work_tag = models.OneToOneField(TagWork, null=False, on_delete=models.CASCADE)
    author = models.CharField(max_length=1000, null=False, blank=False)

    tags = TagField(
        to=TagSong,
        related_name="song_tags"
    )

    history = HistoricalRecords()
    objects = MediaBaseManager()

    class Meta:
        verbose_name = ("Song")
        verbose_name_plural = ("Songs")
        constraints = [
            models.CheckConstraint(
                name="song_bpm_positive",
                check=models.Q(bpm__gt=0),
                violation_error_message="BPM must be positive",
            ),
        ]

    def __str__(self):
        return self.title
        