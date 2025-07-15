from typing import TYPE_CHECKING, cast

import nh3

from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from tagulous.models import TagField, TaggedManager

from .enums import Rating
from .tag import TagWork, TagSong
from otodb.account.models import Account

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from .work_source import WorkSource
    from .pool import PoolItem
    from .relations import WorkRelation

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(moved_to__isnull=True)

# allow setting a through table on tag fields
TagField.forbidden_fields = cast(tuple, tuple(
    v for v in TagField.forbidden_fields if v != "through"
))

class TagWorkInstance(models.Model):
    class Meta:
        unique_together = (("work", "work_tag"),)

    work = models.ForeignKey("MediaWork", on_delete=models.CASCADE)
    work_tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)

    used_as_source = models.BooleanField(null=False, default=False)
    instance_imported_from_source = models.BooleanField(null=False, default=True)


class TagWorkVote(models.Model):
    user = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)
    score = models.FloatField(null=False, blank=False)

    tag_instance = models.ForeignKey(TagWorkInstance, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (("user", "tag_instance"),)
        constraints = [
            models.CheckConstraint(
                name="tagwork_vote_in_pn_1",
                check=models.Q(score__gte=-1, score__lte=1),
                violation_error_message="TagWork vote score must be in [-1, 1]",
            ),
        ]

class MediaWork(models.Model):
    if TYPE_CHECKING:
        worksource_set: QuerySet['WorkSource']
        poolitem_set: QuerySet['PoolItem']
        relation_A: QuerySet['WorkRelation']
        relation_B: QuerySet['WorkRelation']
        tagworkinstance_set: QuerySet['TagWorkInstance']

    title = models.CharField(max_length=1000, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.GENERAL
    )

    tags = TagField(
        to=TagWork,
        related_name="works",
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
        return reverse('otodb:work', kwargs={ 'work_id': self.pk })

    @staticmethod
    # Points work_B to work_A
    def merge(to_work: 'MediaWork', from_work: 'MediaWork', title: str, description: str, thumbnail: str, rating: int):
        to_work.title = title
        to_work.description = description
        to_work.thumbnail = thumbnail
        to_work.rating = rating
        to_work.tags.add(*from_work.tags.all())
        to_work.save()

        for src in from_work.worksource_set.all():
            src.media = to_work
            src.save()

        for item in from_work.poolitem_set.all():
            item.work = to_work
            item.save()

        for relation in from_work.relation_A.all():
            if relation.B.pk == to_work.pk:
                relation.delete()
            else:
                relation.A = to_work
                relation.save()

        for relation in from_work.relation_B.all():
            if relation.A.pk == to_work.pk:
                relation.delete()
            else:
                relation.B = to_work
                relation.save()

        from_work.moved_to = to_work
        from_work.save()

    def save(self, *args, **kwargs):
        if self.description:
            self.description = nh3.clean(self.description)
        super().save(*args, **kwargs)

class MediaSong(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    bpm = models.FloatField(null=False)
    bpm_mixed = models.BooleanField(default=False, null=False)
    work_tag = models.OneToOneField(TagWork, null=False, on_delete=models.CASCADE)
    author = models.CharField(max_length=1000, null=False, blank=False)

    tags = TagField(
        to=TagSong,
        related_name="songs"
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
