from typing import TYPE_CHECKING

from django.db import models
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from .enums import Rating
from .implication import Implication
from .tagged_media import TaggedMedia


class Media(models.Model):
    if TYPE_CHECKING:
        id: int

    parent = models.IntegerField(null=True, blank=True)
    media = models.CharField(max_length=255, null=False, blank=False)
    media_width = models.IntegerField(null=True, blank=True)
    media_height = models.IntegerField(null=True, blank=True)
    tags = TaggableManager(
        through=TaggedMedia,
        related_name="media",
        help_text="A space-separated list of tags."
    )
    tags_mirror = models.CharField(
        max_length=1000,
        blank=True,
        editable=False,
    )

    history = HistoricalRecords()
    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.NONE
    )

    def __str__(self) -> str:
        return f'#{self.id}'

    def save(self, *args, **kwargs):
        super(Media, self).save(*args, **kwargs)

    def get_parent(self):
        if self.parent:
            return Media.objects.filter(parent=self.parent).exclude(id=self.id)
        return None

    def get_children(self):
        return Media.objects.filter(parent=self.id) or None

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

    class Meta:
        verbose_name = ("Media")
        verbose_name_plural = ("Media")
