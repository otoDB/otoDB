from django.db import models
from django.urls import reverse

from otodb.account.models import Account

from .media import MediaWork

class Pool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    author = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'List'
        verbose_name_plural = 'Lists'

    def get_absolute_url(self):
        return reverse('otodb:list', kwargs={ 'list_id': self.id })

    def work_in_pool(self, work_id: int):
        return self.poolitem_set.filter(work_id=work_id)

    def add_work(self, work_id: int):
        if not self.poolitem_set.all():
            order = 1
        else:
            order = self.poolitem_set.aggregate(models.Max('order'))['order__max'] + 1
        work = MediaWork.active_objects.get(id=work_id)
        PoolItem.objects.create(work=work, description='', order=order, pool=self)


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
        constraints = [
            models.UniqueConstraint(fields=["pool", "order"], name="unique_order_in_pool"),
        ]


    def save(self, *args, **kwargs):
        if not self.order:  # Set order only if it's not already set
            max_order = self.pool.poolitem_set.aggregate(max_order=models.Max('order'))['max_order']
            self.order = (max_order or 0) + 1
        super().save(*args, **kwargs)

