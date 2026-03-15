from typing import TYPE_CHECKING, cast

import nh3

from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.functional import cached_property
from tagulous.models import TagField, TaggedManager

from .enums import Rating, WorkTagCategory, Role, FlagStatus, Status
from .tag import TagWork, TagSong, tagwork_ordering_case
from .revision import RevisionTrackedModel

if TYPE_CHECKING:
	from django.db.models import QuerySet
	from .work_source import WorkSource
	from .pool import PoolItem
	from .relations import WorkRelation
	from .moderation import WorkFlag, WorkAppeal, WorkDisapproval


class ActiveManager(models.Manager):
	def get_queryset(self):
		from .moderation import WorkFlag, WorkAppeal

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
			Prefetch(
				'flags',
				queryset=WorkFlag.objects.filter(status=FlagStatus.PENDING)[:1],
				to_attr='pending_flag',
			),
			Prefetch(
				'appeals',
				queryset=WorkAppeal.objects.filter(status=FlagStatus.PENDING)[:1],
				to_attr='pending_appeal',
			),
			'worksource_set',
		)


# allow setting a through table on tag fields
TagField.forbidden_fields = cast(
	tuple, tuple(v for v in TagField.forbidden_fields if v != 'through')
)


class TagWorkInstance(RevisionTrackedModel):
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

	# NOTE: deprecated
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

	class RevisionMeta:
		tracked_fields = ['work', 'work_tag', 'used_as_source', 'creator_roles']
		entity_attrs = ['work']


class TagSongInstance(RevisionTrackedModel):
	class Meta:
		unique_together = (('song', 'song_tag'),)

	song = models.ForeignKey('MediaSong', on_delete=models.CASCADE)
	song_tag = models.ForeignKey(TagSong, on_delete=models.CASCADE)

	class RevisionMeta:
		tracked_fields = ['song', 'song_tag']
		entity_attrs = ['song']


class MediaWork(RevisionTrackedModel):
	if TYPE_CHECKING:
		active_objects: models.Manager['MediaWork']
		worksource_set: QuerySet['WorkSource']
		poolitem_set: QuerySet['PoolItem']
		relation_A: QuerySet['WorkRelation']
		relation_B: QuerySet['WorkRelation']
		tagworkinstance_set: QuerySet['TagWorkInstance']
		flags: QuerySet['WorkFlag']
		appeals: QuerySet['WorkAppeal']
		disapprovals: QuerySet['WorkDisapproval']

	title = models.CharField(max_length=1000, null=True, blank=True)
	description = models.TextField(null=True, blank=True)

	rating = models.IntegerField(choices=Rating.choices, default=Rating.GENERAL)

	tags = TagField(to=TagWork, related_name='works', through=TagWorkInstance)

	thumbnail_source = models.ForeignKey(
		'WorkSource', null=True, blank=True, on_delete=models.SET_NULL
	)

	moved_to = models.ForeignKey(
		'self', null=True, blank=True, on_delete=models.CASCADE
	)

	status = models.IntegerField(choices=Status.choices, default=Status.APPROVED)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)

	class RevisionMeta:
		tracked_fields = ['title', 'description', 'rating', 'moved_to']
		entity_attrs = ['self', 'moved_to']

		def to_active(instance):
			return instance.moved_to or instance

	# deprecated!
	_thumbnail = models.CharField(
		max_length=200,
		null=True,
		blank=True,
		help_text='Deprecated: Use thumbnail_source instead',
	)

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
		from otodb.models.posts import EntityLink

		# Ensure we always merge into the work with the lower ID
		if from_work.pk < to_work.pk:
			to_work, from_work = from_work, to_work

		# Special handling for title: if current is NULL and new is blank, keep NULL
		if to_work.title is None and title == '':
			pass  # Keep title as NULL
		else:
			to_work.title = title
		to_work.description = description
		to_work.thumbnail_source = thumbnail_source
		to_work.rating = rating
		to_work.tags.add(*from_work.tags.all())
		to_work.save()

		from_work.worksource_set.update(media=to_work)

		from_work.poolitem_set.update(work=to_work)

		from_work.relation_A.filter(B=to_work).delete()
		from_work.relation_A.update(A=to_work)

		from_work.relation_B.filter(A=to_work).delete()
		from_work.relation_B.update(B=to_work)

		mediawork_ct = ContentType.objects.get_for_model(MediaWork)

		XtdComment.objects.filter(
			content_type=mediawork_ct, object_pk=str(from_work.pk)
		).update(object_pk=str(to_work.pk))
		EntityLink.objects.filter(
			entity_type=mediawork_ct,
			entity_id=from_work.pk,
			post_id__in=EntityLink.objects.filter(
				entity_type=mediawork_ct,
				entity_id=to_work.pk,
			).values('post_id'),
		).delete()
		EntityLink.objects.filter(
			entity_type=mediawork_ct,
			entity_id=from_work.pk,
		).update(entity_id=to_work.pk)

		from_work.moved_to = to_work
		from_work.save()

	def save(self, *args, **kwargs):
		if self.description:
			self.description = nh3.clean(self.description)
		super().save(*args, **kwargs)

	@cached_property
	def tags_annotated_thin(self):
		twis = list(self.tagworkinstance_set.all())
		t = []
		for instance in twis:
			tag = instance.work_tag
			tag.sample = instance.used_as_source
			tag.creator_roles = instance.creator_roles
			t.append(tag)
		return t

	@cached_property
	def tags_annotated(self):
		twis = list(self.tagworkinstance_set.filter(work_tag__deprecated=False))
		primary_paths = TagWork.get_primary_paths([i.work_tag_id for i in twis])
		t = []
		for instance in twis:
			tag = instance.work_tag
			tag.sample = instance.used_as_source
			tag.creator_roles = instance.creator_roles
			tag.primary_path = primary_paths.get(tag.id, [])
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


class MediaSong(RevisionTrackedModel):
	title = models.CharField(max_length=1000, null=False, blank=False)
	bpm = models.FloatField(null=True)
	variable_bpm = models.BooleanField(default=False, null=False)
	work_tag = models.OneToOneField(TagWork, null=False, on_delete=models.CASCADE)
	author = models.CharField(max_length=1000, null=False, blank=False)

	tags = TagField(to=TagSong, related_name='songs', through=TagSongInstance)

	class RevisionMeta:
		tracked_fields = ['title', 'bpm', 'variable_bpm', 'work_tag', 'author']
		entity_attrs = ['self', 'work_tag']

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
