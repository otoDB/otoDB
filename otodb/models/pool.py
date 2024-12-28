from django.db import models
from simple_history.models import HistoricalRecords

from otodb.account.models import Account

from .media_work import MediaWork


class Pool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    history = HistoricalRecords()
    author = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'List'
        verbose_name_plural = 'Lists'

class PoolItem(models.Model):
    work = models.ForeignKey(MediaWork, blank=False, null=False, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.work}'

    class Meta:
        verbose_name = 'List Entry'
        verbose_name_plural = 'List Entries'
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.order:  # Set order only if it's not already set
            max_order = PoolItem.objects.filter(pool=self.pool).aggregate(max_order=models.Max('order'))['max_order']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)
