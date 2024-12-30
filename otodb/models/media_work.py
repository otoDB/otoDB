from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from simple_history.models import HistoricalRecords
from tagulous.models import TagField

from .base import MediaBase, MediaBaseManager
from .enums import Rating
from .tag_main import TagWork


class MediaWork(MediaBase):
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=1000, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.NONE
    )

    tags = TagField(
        to=TagWork,
        related_name="work_tags"
    )

    thumbnail = models.CharField(max_length=200, null=True, blank=True)

    history = HistoricalRecords()
    objects: MediaBaseManager

    def clean(self):
        if self.parent == self:
            raise ValidationError('Work cannot be set as parent of itself')

    def get_parent(self):
        if self.parent:
            return MediaWork.objects.filter(parent=self.parent).exclude(id=self.id)
        return None

    def get_children(self):
        return MediaWork.objects.filter(parent=self.id) or None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Work")
        verbose_name_plural = ("Works")
        constraints = [
            models.CheckConstraint(
                name='work_prevent_self_parent',
                check=~Q(parent=F('id'))
            )
        ]

    def get_absolute_url(self):
        return reverse('otodb:work', kwargs={ 'work_id': self.id })
