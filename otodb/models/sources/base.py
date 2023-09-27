from django.db import models

from ..media_source import MediaSource


class SourceMediaBase(models.Model):
    media_source = models.OneToOneField(MediaSource, on_delete=models.CASCADE)
