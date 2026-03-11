from typing import TYPE_CHECKING, Self
from itertools import chain

from django.db import models
from django.db.models import Value, Q, Prefetch
from tagulous.models import BaseTagModel, TagModelManager

from django_cte import CTE, with_cte

from .enums import WorkTagCategory, SongTagCategory, LanguageTypes, MediaType
from .revision import RevisionTrackedModel, RevisionTrackedManager

if TYPE_CHECKING:
	from django.db.models import QuerySet
	from .connection import (
		TagWorkConnection,
		TagWorkMediaConnection,
		TagWorkCreatorConnection,
	)
	from .media import MediaSong


def name_cleaner(s):
	return s.lower()


def tagwork_ordering_case(prefix=''):
	prefix = f'{prefix}__' if prefix and not prefix.endswith('__') else prefix
	return models.Case(
		models.When(
			**{f'{prefix}category': WorkTagCategory.EVENT}, then=models.Value(0)
		),
		models.When(
			**{f'{prefix}category': WorkTagCategory.CREATOR}, then=models.Value(10)
		),
		models.When(
			**{f'{prefix}category': WorkTagCategory.MEDIA}, then=models.Value(11)
		),
		models.When(
			**{f'{prefix}category': WorkTagCategory.SOURCE}, then=models.Value(20)
		),
		models.When(
			**{f'{prefix}category': WorkTagCategory.SONG}, then=models.Value(30)
		),
		models.When(
			**{f'{prefix}category': WorkTagCategory.GENERAL}, then=models.Value(40)
		),
		models.When(
			**{f'{prefix}category': WorkTagCategory.META}, then=models.Value(1000)
		),
		default=models.Value(999),
		output_field=models.IntegerField(),
	)


class LowerCaseTagModelManager(RevisionTrackedManager, TagModelManager):
	"""Base manager that handles lowercase name normalization for all tag models"""

	def get_or_create(self, *args, **kwargs):
		if 'name' in kwargs:
			kwargs['name'] = name_cleaner(kwargs['name'])
		return super().get_or_create(*args, **kwargs)

	def get(self, *args, **kwargs):
		if 'name' in kwargs:
			kwargs['name'] = name_cleaner(kwargs['name'])
		return super().get(*args, **kwargs)


class TagWorkManager(LowerCaseTagModelManager):
	def get_queryset(self):
		# Prefetch language preferences with their tag relationship
		lang_prefs_qs = TagWorkLangPreference.objects.select_related('tag')

		# For aliases, use parent's get_queryset to avoid infinite recursion
		aliases_base_qs = super(TagWorkManager, self).get_queryset()

		return (
			super()
			.get_queryset()
			.select_related('aliased_to')
			.prefetch_related(
				Prefetch('tagworklangpreference_set', queryset=lang_prefs_qs),
				Prefetch(
					'aliases',
					queryset=aliases_base_qs.prefetch_related(
						Prefetch('tagworklangpreference_set', queryset=lang_prefs_qs)
					),
				),
			)
		)


class TagSongManager(LowerCaseTagModelManager):
	def get_queryset(self):
		# Prefetch language preferences with their tag relationship
		lang_prefs_qs = TagSongLangPreference.objects.select_related('tag')

		# For aliases, use parent's get_queryset to avoid infinite recursion
		aliases_base_qs = super(TagSongManager, self).get_queryset()

		return (
			super()
			.get_queryset()
			.prefetch_related('children')
			.select_related('aliased_to')
			.prefetch_related(
				Prefetch('tagsonglangpreference_set', queryset=lang_prefs_qs),
				Prefetch(
					'aliases',
					queryset=aliases_base_qs.prefetch_related(
						Prefetch('tagsonglangpreference_set', queryset=lang_prefs_qs)
					),
				),
			)
		)


class OtodbTagModel(BaseTagModel):
	"""
	Abstract base class for tag models
	"""

	name = models.CharField(unique=True, max_length=255)
	slug = models.SlugField(unique=True, max_length=255, allow_unicode=True)
	count = models.IntegerField(
		default=0, help_text='Internal counter of how many times this tag is in use'
	)
	protected = models.BooleanField(
		default=False, help_text='Will not be deleted when the count reaches 0'
	)
	aliased_to = models.ForeignKey(
		'self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases'
	)

	def save(self, *args, **kwargs):
		if self.name:
			self.name = name_cleaner(self.name)
		super().save(*args, **kwargs)

	class Meta:
		abstract = True
		ordering = ('name',)

	@classmethod
	def alias(cls, from_tags: list[Self], into_tag: Self):
		from django.contrib.contenttypes.models import ContentType
		from django_comments_xtd.models import XtdComment

		self_ct = ContentType.objects.get_for_model(cls)
		for tag in from_tags:
			if tag.aliased_to:
				tag = tag.aliased_to
			if tag.id != into_tag.id:
				tag.aliased_to = into_tag
				tag.save()
				cls.transfer_data(tag, into_tag)
				cls.objects.filter(aliased_to=tag).update(aliased_to=into_tag)
				XtdComment.objects.filter(
					content_type=self_ct, object_pk=str(tag.pk)
				).update(object_pk=str(into_tag.pk))


class TagWork(RevisionTrackedModel, OtodbTagModel):
	objects = TagWorkManager()

	if TYPE_CHECKING:
		tagworkconnection_set: QuerySet['TagWorkConnection']
		tagworkmediaconnection_set: QuerySet['TagWorkMediaConnection']
		tagworkcreatorconnection_set: QuerySet['TagWorkCreatorConnection']
		tagworklangpreference_set: QuerySet['TagWorkLangPreference']
		aliases: QuerySet['TagWork']
		mediasong: 'MediaSong | None'
		childhood: QuerySet['TagWorkParenthood']
		parenthood: QuerySet['TagWorkParenthood']
		wikipage_set: QuerySet['WikiPage']

	class TagMeta:
		protect_all = True
		case_sensitive = False
		force_lowercase = True

	class Meta:
		ordering = [
			tagwork_ordering_case(),
			'name',
		]

	deprecated = models.BooleanField(default=False, null=False)
	category = models.IntegerField(
		choices=WorkTagCategory.choices, default=WorkTagCategory.GENERAL
	)
	media_type = models.IntegerField(
		null=True, blank=True, help_text='Media type bitmask'
	)

	class RevisionMeta:
		tracked_fields = [
			'name',
			'slug',
			'aliased_to',
			'deprecated',
			'category',
			'media_type',
		]
		entity_attrs = ['self', 'aliased_to']

		def to_active(instance):
			return instance.aliased_to or instance

	@property
	def display_name(self):
		return self.name.replace('_', ' ')

	def __str__(self):
		return self.name

	def get_song(self):
		if self.mediasong is not None:
			return self.mediasong

	def set_media_type(self, types: list[MediaType | int]):
		if self.category != WorkTagCategory.MEDIA:
			self.media_type = None
			return

		type_value = 0
		for t in types:
			if isinstance(t, MediaType):
				type_value |= t.value
			else:
				type_value |= t
		self.media_type = type_value if type_value > 0 else None

	@property
	def lang_prefs(self):
		if self.aliased_to:
			return self.aliased_to.lang_prefs

		prefs_dict = {}
		for pref in self.tagworklangpreference_set.all():
			prefs_dict[pref.pk] = pref
		for alias in self.aliases.all():
			for pref in alias.tagworklangpreference_set.all():
				prefs_dict[pref.pk] = pref

		return list(prefs_dict.values())

	@property
	def unaliasable(self):
		return any(
			[
				self.wikipage_set.exists()
				and any([p.page.strip() != '' for p in self.wikipage_set]),
				self.tagworkconnection_set.exists(),
				self.category != WorkTagCategory.GENERAL,
			]
		)

	@property
	def can_be_deleted(self):
		# Maximal friction to avoid accidentally deleting any user-contributed data
		return not any(
			[
				self.unaliasable,
				self.works.exists(),
				self.aliased_to,
				self.aliases.exists(),
			]
		)

	@property
	def children(self):
		return TagWork.objects.filter(childhood__parent=self, aliased_to__isnull=True)

	def get_descendants(self):
		cte = CTE.recursive(
			lambda cte: (
				TagWork.objects.order_by()
				.filter(id=self.id)
				.values('id')
				.union(
					cte.join(
						TagWork.objects.order_by(),
						childhood__parent_id=cte.col.id,
						aliased_to__isnull=True,
						deprecated=False,
					).values('id'),
					all=True,
				)
			)
		)
		return (
			with_cte(cte, select=cte.join(TagWork, id=cte.col.id))
			.exclude(id=self.id)
			.distinct()
			.order_by()
		)

	def get_paths(self):
		cte = CTE.recursive(
			lambda cte: (
				TagWork.objects.order_by()
				.filter(id=self.id)
				.values(
					'id',
					'slug',
					fr=Value('', output_field=models.TextField()),
				)
				.union(
					cte.join(
						TagWork.objects.order_by(),
						parenthood__tag_id=cte.col.id,
						aliased_to__isnull=True,
						deprecated=False,
					).values(
						'id',
						'slug',
						fr=models.functions.Cast(cte.col.slug, models.TextField()),
					),  # Cannot do all=True because we could have diamond problems
				)
			)
		)
		return with_cte(
			cte, select=cte.join(TagWork, id=cte.col.id).annotate(fr=cte.col.fr)
		).order_by()

	@classmethod
	def get_primary_paths(cls, tag_ids: list[int]) -> dict[int, list[Self]]:
		if not tag_ids:
			return {}

		cte = CTE.recursive(
			lambda cte: (
				cls.objects.order_by()
				.filter(id__in=tag_ids)
				.values(
					'id',
					source_tag_id=models.F('id'),
					depth=Value(0, output_field=models.IntegerField()),
				)
				.union(
					cte.join(
						cls.objects.order_by(),
						parenthood__tag_id=cte.col.id,
						parenthood__primary=True,
						aliased_to__isnull=True,
						deprecated=False,
					).values(
						'id',
						source_tag_id=cte.col.source_tag_id,
						depth=cte.col.depth
						+ Value(1, output_field=models.IntegerField()),
					),
					all=True,
				)
			)
		)

		results = with_cte(
			cte,
			select=cte.join(cls, id=cte.col.id).annotate(
				source_tag_id=cte.col.source_tag_id, depth=cte.col.depth
			),
		).order_by('source_tag_id', '-depth')

		paths_dict = {}
		for tag in results:
			if tag.id != tag.source_tag_id:
				if tag.source_tag_id not in paths_dict:
					paths_dict[tag.source_tag_id] = []
				paths_dict[tag.source_tag_id].append(tag)

		return paths_dict

	@classmethod
	def transfer_data(cls, from_tag: Self, to_tag: Self):
		from .media import TagWorkInstance

		# transfer/merge TagWorkInstance records (creator_roles, used_as_source, etc.)
		for twi in TagWorkInstance.objects.filter(work_tag=from_tag):
			# check if the work already has the `to_tag` associated
			existing_twi = TagWorkInstance.objects.filter(
				work=twi.work, work_tag=to_tag
			).first()

			if existing_twi:
				# merge the attributes
				if twi.creator_roles:
					if existing_twi.creator_roles:
						# combine role bitmasks
						existing_twi.creator_roles |= twi.creator_roles
					else:
						existing_twi.creator_roles = twi.creator_roles

				if twi.used_as_source:
					existing_twi.used_as_source = True

				# keep instance_imported_from_source as True if either is True
				if (
					twi.instance_imported_from_source
					or existing_twi.instance_imported_from_source
				):
					existing_twi.instance_imported_from_source = True

				existing_twi.save()
				twi.delete()
			else:
				# if no existing instance, just transfer
				twi.work_tag = to_tag
				twi.save()

		# carry over parenthood, category, wikipages, connections
		for tp in TagWorkParenthood.objects.filter(parent=from_tag):
			if TagWorkParenthood.objects.filter(tag=tp.tag, parent=to_tag).exists():
				tp.delete()
			elif not to_tag.get_paths().filter(id=tp.tag.id).exists():
				tp.parent = to_tag
				tp.save()
			else:
				tp.delete()
		for tp in TagWorkParenthood.objects.filter(tag=from_tag):
			if TagWorkParenthood.objects.filter(parent=tp.parent, tag=to_tag).exists():
				tp.delete()
			elif not to_tag.get_descendants().filter(id=tp.tag.id).exists():
				tp.tag = to_tag
				tp.save()
			else:
				tp.delete()
		if (
			from_tag.category != WorkTagCategory.GENERAL
			and to_tag.category == WorkTagCategory.GENERAL
		):
			to_tag.category = from_tag.category
			if from_tag.category == WorkTagCategory.MEDIA:
				to_tag.media_type = from_tag.media_type
				from_tag.media_type = None
			if from_tag.category == WorkTagCategory.SONG:
				s = from_tag.mediasong
				s.work_tag = to_tag
				s.save()
			from_tag.category = WorkTagCategory.GENERAL
			from_tag.save()
		for p in from_tag.wikipage_set.all():
			try:
				page = WikiPage.objects.get(tag=to_tag, lang=p.lang)
				page.page += '\n\n'
				page.page += p.page
				page.save()
			except WikiPage.DoesNotExist:
				WikiPage.objects.create(tag=to_tag, lang=p.lang, page=p.page)
			p.delete()
		for c in chain(
			from_tag.tagworkconnection_set.all(),
			from_tag.tagworkmediaconnection_set.all(),
			from_tag.tagworkcreatorconnection_set.all(),
		):
			if (
				type(c)
				.objects.filter(tag=to_tag, site=c.site, content_id=c.content_id)
				.exists()
			):
				c.delete()
			else:
				c.tag = to_tag
				c.save()
		to_tag.save()


class TagWorkLangPreference(RevisionTrackedModel):
	lang = models.IntegerField(
		choices=LanguageTypes.choices,
		default=LanguageTypes.NOT_APPLICABLE,
		null=False,
		blank=False,
	)
	tag = models.ForeignKey(TagWork, null=False, blank=False, on_delete=models.CASCADE)

	class RevisionMeta:
		tracked_fields = ['lang', 'tag']
		entity_attrs = ['tag']

	class Meta:
		unique_together = (('tag', 'lang'),)


class WikiPage(RevisionTrackedModel):
	tag = models.ForeignKey(TagWork, on_delete=models.CASCADE, null=False, blank=False)
	page = models.TextField(null=False)
	lang = models.IntegerField(
		choices=LanguageTypes.choices,
		default=LanguageTypes.NOT_APPLICABLE,
		null=False,
		blank=False,
	)

	class RevisionMeta:
		tracked_fields = ['lang', 'tag', 'page']
		entity_attrs = ['tag']

	class Meta:
		unique_together = (('tag', 'lang'),)


class TagSong(RevisionTrackedModel, OtodbTagModel):
	objects = TagSongManager()

	class TagMeta:
		protect_all = True
		case_sensitive = False
		force_lowercase = True

	category = models.IntegerField(
		choices=SongTagCategory.choices, default=SongTagCategory.GENERAL
	)
	parent = models.ForeignKey(
		'self',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='children',
	)

	class RevisionMeta:
		tracked_fields = ['name', 'slug', 'aliased_to', 'category', 'parent']
		entity_attrs = ['self']

		def to_active(instance):
			return instance.aliased_to or instance

	class Meta:
		constraints = [
			models.CheckConstraint(
				name='tagsong_parenthood_nonreflexive',
				condition=~Q(parent_id=models.F('id')),
				violation_error_message='tag cannot be own parent',
			),
		]

	@property
	def display_name(self):
		return self.name.replace('_', ' ')

	def __str__(self):
		return self.name

	@classmethod
	def transfer_data(cls, from_tag: Self, to_tag: Self):
		for song in from_tag.songs.all():
			song.tags.add(to_tag)
			song.tags.remove(from_tag)
		cls.objects.filter(parent=from_tag).update(parent=to_tag)

		# carry over category and parenthood
		for tc in from_tag.children.all():
			if not to_tag.get_tree().filter(id=tc.id).exists():
				tc.parent = to_tag
			else:
				tc.parent = None
			tc.save()
		if tp := from_tag.parent:
			if not to_tag.get_descendants().filter(id=tp.id).exists():
				to_tag.parent = tp
				to_tag.save()
			from_tag.parent = None
			from_tag.save()
		if (
			from_tag.category != SongTagCategory.GENERAL
			and to_tag.category == SongTagCategory.GENERAL
		):
			to_tag.category = from_tag.category
			from_tag.category = SongTagCategory.GENERAL
			from_tag.save()

		to_tag.save()

	@property
	def can_be_deleted(self):
		return not any(
			[
				self.category != SongTagCategory.GENERAL,
				self.songs.exists(),
				self.aliased_to,
				self.aliases.exists(),
			]
		)

	def get_tree(self):
		cte = CTE.recursive(
			lambda cte: (
				TagSong.objects.order_by()
				.filter(id=self.id)
				.values(
					'id',
					'parent_id',
					depth=Value(0, output_field=models.IntegerField()),
				)
				.union(
					cte.join(TagSong.objects.order_by(), id=cte.col.parent_id).values(
						'id',
						'parent_id',
						depth=cte.col.depth
						+ Value(1, output_field=models.IntegerField()),
					),
					all=True,
				)
			)
		)
		return with_cte(
			cte, select=cte.join(TagSong, id=cte.col.id).annotate(depth=cte.col.depth)
		).order_by('-depth')

	def get_descendants(self):
		cte = CTE.recursive(
			lambda cte: (
				TagSong.objects.order_by()
				.filter(id=self.id)
				.values('id')
				.union(
					cte.join(
						TagSong.objects.order_by(),
						parent_id=cte.col.id,
						aliased_to__isnull=True,
					).values('id'),
					all=True,
				)
			)
		)
		return (
			with_cte(cte, select=cte.join(TagSong, id=cte.col.id))
			.exclude(id=self.id)
			.distinct()
			.order_by()
		)

	@property
	def lang_prefs(self):
		if self.aliased_to:
			return self.aliased_to.lang_prefs

		prefs_dict = {}
		for pref in self.tagsonglangpreference_set.all():
			prefs_dict[pref.pk] = pref
		for alias in self.aliases.all():
			for pref in alias.tagsonglangpreference_set.all():
				prefs_dict[pref.pk] = pref

		return list(prefs_dict.values())


class TagSongLangPreference(RevisionTrackedModel):
	lang = models.IntegerField(
		choices=LanguageTypes.choices,
		default=LanguageTypes.NOT_APPLICABLE,
		null=False,
		blank=False,
	)
	tag = models.ForeignKey(TagSong, null=False, blank=False, on_delete=models.CASCADE)

	class RevisionMeta:
		tracked_fields = ['lang', 'tag']
		entity_attrs = ['tag']

	class Meta:
		unique_together = (('tag', 'lang'),)


class TagWorkParenthood(RevisionTrackedModel):
	tag = models.ForeignKey(
		TagWork,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='childhood',
	)
	parent = models.ForeignKey(
		TagWork,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='parenthood',
	)
	primary = models.BooleanField(default=False)

	class RevisionMeta:
		tracked_fields = ['tag', 'parent', 'primary']
		entity_attrs = ['tag', 'parent']

	class Meta:
		unique_together = (('tag', 'parent'),)
		constraints = [
			models.CheckConstraint(
				name='tagwork_parenthood_nonreflexive',
				condition=~Q(tag=models.F('parent')),
				violation_error_message='tag cannot be own parent',
			),
			models.UniqueConstraint(
				fields=['tag'],
				condition=Q(primary=True),
				name='tagwork_parenthood_at_most_one_primary',
			),
		]
