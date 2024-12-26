from django.db import models

from .base import SourceWorkBase


class SourceWorkYouTube(SourceWorkBase):
    source_id = models.CharField(max_length=16)
    likes = models.IntegerField(null=True, blank=True)
    dislikes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'YouTube'
