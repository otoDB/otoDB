from django.db import models

from .base import SourceWorkBase


class SourceWorkBilibili(SourceWorkBase):
    source_id = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.work_source.published_date} @ Bilibili'
