from django.db import models
from simple_history.models import HistoricalRecords

from .enums import PoolCategory
from .media_work import MediaWork


class Pool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    works = models.ManyToManyField(MediaWork, blank=True)
    status = models.IntegerField(
        choices=PoolCategory.choices,
        default=PoolCategory.COLLECTION
    )

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'Pool'
        verbose_name_plural = 'Pools'
