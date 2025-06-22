from django.db import models
from django.urls import reverse

from ordered_model.models import OrderedModel

from otodb.account.models import Account

from .media import MediaWork

class Pool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    author = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)

    pending_items = models.ManyToManyField('WorkSource')

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
        PoolItem.objects.create(work_id=work_id, description='', pool=self)

class PoolItem(OrderedModel):
    work = models.ForeignKey(MediaWork, blank=False, null=False, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, blank=False, null=False)
    description = models.TextField(null=True, blank=True)

    order_with_respect_to = 'pool'

    def __str__(self) -> str:
        return f'{self.work}'

    class Meta(OrderedModel.Meta):
        verbose_name = 'List Entry'
        verbose_name_plural = 'List Entries'

class PoolUpstream(models.Model):
    pool = models.OneToOneField(Pool, null=False, on_delete=models.CASCADE)
    upstream = models.URLField(null=False, blank=False)
