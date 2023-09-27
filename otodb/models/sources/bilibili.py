from django.db import models

from .base import SourceMediaBase


class SourceMediaBilibili(SourceMediaBase):
    source_id = models.CharField(max_length=10)
