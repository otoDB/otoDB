from django.db import models

from .base import SourceMediaBase


class SourceMediaSoundCloud(SourceMediaBase):
    source_id = models.CharField(max_length=1000)
