from django.db import models

from .base import SourceWorkBase


class SourceWorkSoundCloud(SourceWorkBase):
    source_id = models.CharField(max_length=1000)
