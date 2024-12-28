import random
from typing import TYPE_CHECKING

from django.db import models

from .implication import Implication


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

    tags_mirror = models.CharField(
        max_length=1000,
        blank=True,
        editable=False,
    )

    objects = MediaBaseManager()

    def __str__(self) -> str:
        return f'{self._meta.verbose_name} #{self.id}'

    def check_and_update_mirror(self, record_history=False):
        mirror = " ".join(self.tags.names())

        if self.tags_mirror != mirror:
            self.tags_mirror = mirror
        else:
            return

        if record_history:
            self.save()
        else:
            self.save_without_historial_record()

    def save_without_historial_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

    def check_and_update_implications(self):
        missing_implications = Implication.objects.filter(
            from_tag__in=self.tags.all(), status=1
        ).exclude(to_tag__in=self.tags.all()).distinct()

        if missing_implications.exists():
            for impl in missing_implications:
                self.tags.add(impl.to_tag)

        self.check_and_update_mirror()
