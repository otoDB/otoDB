from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from tagulous.models import TagField, TaggedManager

from .enums import Rating
from .tag import TagWork, TagSong
from otodb.account.models import Account

import random

class ActiveManager(models.Manager):
    def random(self):
        random_work = None
        work_ids = self.values_list('pk', flat=True)
        if work_ids:
            random_work = self.get(pk=random.choice(work_ids))
            if random_work.moved_to:
                random_work = random_work.moved_to
            return random_work

    def get_queryset(self):
        return super().get_queryset().filter(moved_to__isnull=True)


# allow setting a through table on tag fields
TagField.forbidden_fields = tuple(
    v for v in TagField.forbidden_fields if v != "through"
)

class TagWorkInstance(models.Model):
    class Meta:
        unique_together = (("work", "work_tag"),)

    work = models.ForeignKey("MediaWork", on_delete=models.CASCADE)
    work_tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)

    mean_score = models.FloatField(null=False, blank=False, default=0.0)

    song_used_as_source = models.BooleanField(null=False, default=False)
    instance_imported_from_source = models.BooleanField(null=False, default=False)


class TagWorkVote(models.Model):
    user = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)
    score = models.FloatField(null=False, blank=False)

    tag_instance = models.ForeignKey(TagWorkInstance, on_delete=models.CASCADE, null=True)

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

    moved_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    objects = models.Manager()
    active_objects = TaggedManager.cast_class(ActiveManager())

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("Work")
        verbose_name_plural = ("Works")

    def get_absolute_url(self):
        return reverse('otodb:work', kwargs={ 'work_id': self.id })

class MediaSong(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    bpm = models.FloatField(null=False)
    work_tag = models.OneToOneField(TagWork, null=False, on_delete=models.CASCADE)
    author = models.CharField(max_length=1000, null=False, blank=False)

    tags = TagField(
        to=TagSong,
        related_name="song_tags"
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Song")
        verbose_name_plural = ("Songs")
        constraints = [
            models.CheckConstraint(
                name="song_bpm_positive",
                check=models.Q(bpm__gt=0),
                violation_error_message="BPM must be positive",
            ),
        ]

    def __str__(self):
        return self.title
