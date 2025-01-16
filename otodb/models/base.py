import random
from typing import TYPE_CHECKING

from django.db import models

class MediaBaseManager(models.Manager):
    def random(self):
        random_work = None
        work_ids = self.values_list('pk', flat=True)
        if work_ids:
            random_work = self.get(pk=random.choice(work_ids))
            return random_work

class MediaBase(models.Model):
    if TYPE_CHECKING:
        id: int

    class Meta:
        verbose_name = 'Item'
        abstract = True

    objects = MediaBaseManager()

    def __str__(self) -> str:
        return f'{self._meta.verbose_name} #{self.id}'

    def save_without_historial_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret
