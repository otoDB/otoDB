from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from simple_history.models import HistoricalRecords
from tagulous.models import TagField

from .base import MediaBaseManager
from .enums import Rating
from .tag import TagWork

class MediaWork(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.GENERAL
    )

    tags = TagField(
        to=TagWork,
        related_name="work_tags"
    )

    thumbnail = models.CharField(max_length=200, null=True, blank=True)

    history = HistoricalRecords(m2m_fields=[tags])

    objects = MediaBaseManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Work")
        verbose_name_plural = ("Works")

    def get_absolute_url(self):
        return reverse('otodb:work', kwargs={ 'work_id': self.id })
