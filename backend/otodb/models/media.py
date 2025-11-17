from typing import TYPE_CHECKING, cast

import nh3

from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.functional import cached_property
from simple_history.models import HistoricalRecords
from tagulous.models import TagField, TaggedManager

from .enums import Rating, WorkTagCategory, Role
from .tag import TagWork, TagSong, tagwork_ordering_case

if TYPE_CHECKING:
	from django.db.models import QuerySet
	from .work_source import WorkSource
	from .pool import PoolItem
	from .relations import WorkRelation


class ActiveManager(models.Manager):
	def get_queryset(self):
		qs = super().get_queryset().filter(moved_to__isnull=True)

		instances_queryset = (
			TagWorkInstance.objects.filter(work_tag__deprecated=False)
			.select_related(
				'work_tag',
				'work_tag__aliased_to',
			)
			.prefetch_related(
				'work_tag__tagworklangpreference_set',
				'work_tag__aliases',
				'work_tag__aliases__tagworklangpreference_set',
			)
			.order_by(
				tagwork_ordering_case(prefix='work_tag__'),
				'work_tag__name',
			)
		)

		return qs.select_related('thumbnail_source').prefetch_related(
			Prefetch('tagworkinstance_set', queryset=instances_queryset),
			'worksource_set',
		)


# allow setting a through table on tag fields
TagField.forbidden_fields = cast(
	tuple, tuple(v for v in TagField.forbidden_fields if v != 'through')
)


class TagWorkInstance(models.Model):
	if TYPE_CHECKING:
		work_id: int
		work_tag_id: int

	class Meta:
		unique_together = (('work', 'work_tag'),)

	work = models.ForeignKey('MediaWork', on_delete=models.CASCADE)
	work_tag = models.ForeignKey(TagWork, on_delete=models.CASCADE)

	used_as_source = models.BooleanField(null=False, default=False)
	creator_roles = models.IntegerField(
		null=True, blank=True, help_text='Creator role bitmask'
	)
	instance_imported_from_source = models.BooleanField(null=False, default=True)

	def set_creator_roles(self, roles: list[Role | int]):
		if self.work_tag.category != WorkTagCategory.CREATOR:
			self.creator_roles = None
			return

		role_value = 0
		for role in roles:
			if isinstance(role, Role):
				role_value |= role.value
			else:
				role_value |= role
		self.creator_roles = role_value if role_value > 0 else None


class MediaWork(models.Model):
	if TYPE_CHECKING:
		worksource_set: QuerySet['WorkSource']
		poolitem_set: QuerySet['PoolItem']
		relation_A: QuerySet['WorkRelation']
		relation_B: QuerySet['WorkRelation']
		tagworkinstance_set: QuerySet['TagWorkInstance']

	title = models.CharField(max_length=1000, null=True, blank=True)
	description = models.TextField(null=True, blank=True)

	rating = models.IntegerField(choices=Rating.choices, default=Rating.GENERAL)

	tags = TagField(to=TagWork, related_name='works', through=TagWorkInstance)

	thumbnail_source = models.ForeignKey(
		'WorkSource', null=True, blank=True, on_delete=models.SET_NULL
	)

	history = HistoricalRecords(m2m_fields=[tags])

	moved_to = models.ForeignKey(
		'self', null=True, blank=True, on_delete=models.CASCADE
	)

	# deprecated!
	_thumbnail = models.CharField(
		max_length=200,
		null=True,
		blank=True,
		help_text='Deprecated: Use thumbnail_source instead',
	)

	objects = models.Manager()
	active_objects = TaggedManager.cast_class(ActiveManager())

	def __str__(self):
		return f'{self.pk}: {self.title}'

	class Meta:
		verbose_name = 'Work'
		verbose_name_plural = 'Works'
		ordering = ['-id']

	def get_absolute_url(self):
		return reverse('otodb:work', kwargs={'work_id': self.pk})

	@staticmethod
	# Points work_B to work_A
	def merge(
		to_work: 'MediaWork',
		from_work: 'MediaWork',
		title: str,
		description: str,
		thumbnail_source: 'WorkSource',
		rating: int,
	):
		from django.contrib.contenttypes.models import ContentType
		from django_comments_xtd.models import XtdComment

		# Ensure we always merge into the work with the lower ID
		if from_work.pk < to_work.pk:
			to_work, from_work = from_work, to_work

		to_work.title = title
		to_work.description = description
		to_work.thumbnail_source = thumbnail_source
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

		mediawork_ct = ContentType.objects.get_for_model(MediaWork)
		XtdComment.objects.filter(
			content_type=mediawork_ct, object_pk=str(from_work.pk)
		).update(object_pk=str(to_work.pk))

		from_work.moved_to = to_work
		from_work.save()

	def save(self, *args, **kwargs):
		if self.description:
			self.description = nh3.clean(self.description)
		super().save(*args, **kwargs)

	@cached_property
	def tags_annotated(self):
		t = []
		for instance in self.tagworkinstance_set.all():
			tag = instance.work_tag
			tag.sample = instance.used_as_source
			tag.creator_roles = instance.creator_roles
			t.append(tag)
		return t

	@property
	def thumbnail(self):
		thumbnail = self.thumbnail_source.thumbnail if self.thumbnail_source else None
		if not thumbnail:
			# Fallback to first source thumbnail
			first_source = self.worksource_set.first()
			if first_source:
				thumbnail = first_source.thumbnail
		# Fallback to deprecated field (3rd-party remote URL)
		return thumbnail or self._thumbnail

	@property
	def relations(self):
		rs = self.relation_A.all() | self.relation_B.all()
		return rs, MediaWork.active_objects.filter(
			id__in=[
				*rs.values_list('A_id', flat=True),
				*rs.values_list('B_id', flat=True),
			]
		).exclude(id=self.pk)


class MediaSong(models.Model):
	title = models.CharField(max_length=1000, null=False, blank=False)
	bpm = models.FloatField(null=True)
	variable_bpm = models.BooleanField(default=False, null=False)
	work_tag = models.OneToOneField(TagWork, null=False, on_delete=models.CASCADE)
	author = models.CharField(max_length=1000, null=False, blank=False)

	tags = TagField(to=TagSong, related_name='songs')

	history = HistoricalRecords(m2m_fields=[tags])

	class Meta:
		verbose_name = 'Song'
		verbose_name_plural = 'Songs'
		constraints = [
			models.CheckConstraint(
				name='song_bpm_positive',
				condition=models.Q(bpm__gt=0),
				violation_error_message='BPM must be positive',
			),
		]

	def __str__(self):
		return self.title
