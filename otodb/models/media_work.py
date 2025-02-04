from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from tagulous.models import TagField

from .base import MediaBaseManager
from .enums import Rating
from .tag import TagWork

# allow setting a through table on tag fields
TagField.forbidden_fields = tuple(
    v for v in TagField.forbidden_fields if v != "through"
)

class TagWorkInstance(models.Model):
    class Meta:
        unique_together = (("work", "work_tag"),)

    work = models.ForeignKey("MediaWork", on_delete=models.CASCADE)
    work_tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)

    score = models.FloatField(null=True)

class MediaWork(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.GENERAL
    )

    tags = TagField(
        to=TagWork,
        related_name="work_tags",
        through=TagWorkInstance
    )

    thumbnail = models.CharField(max_length=200, null=True, blank=True)

    history = HistoricalRecords(m2m_fields=[tags])

    objects = MediaBaseManager()

    moved_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Work")
        verbose_name_plural = ("Works")

    def get_absolute_url(self):
        return reverse('otodb:work', kwargs={ 'work_id': self.id })
