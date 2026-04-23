from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.urls import reverse
from ordered_model.models import OrderedModel

from .media import MediaWork


class Pool(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(null=True, blank=True)

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL, blank=False, null=False, on_delete=models.CASCADE
	)

	pending_items = models.ManyToManyField('WorkSource')

	if TYPE_CHECKING:
		from django.db.models import QuerySet

		poolitem_set: QuerySet['PoolItem']

	def __str__(self) -> str:
		return f'{self.name}'

	class Meta:
		verbose_name = 'List'
		verbose_name_plural = 'Lists'

	def get_absolute_url(self):
		return reverse('otodb:list', kwargs={'list_id': self.pk})

	def work_in_pool(self, work_id: int):
		return self.poolitem_set.filter(work_id=work_id)

	def add_work(self, work_id: int):
		PoolItem.objects.create(work_id=work_id, description='', pool=self)


class PoolItem(OrderedModel):
	work = models.ForeignKey(
		MediaWork, blank=False, null=False, on_delete=models.CASCADE
	)
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
