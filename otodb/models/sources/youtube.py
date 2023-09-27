from django.db import models

from .base import SourceMediaBase


class SourceMediaYouTube(SourceMediaBase):
    source_id = models.CharField(max_length=16)
    likes = models.IntegerField(null=True, blank=True)
    dislikes = models.IntegerField(null=True, blank=True)
