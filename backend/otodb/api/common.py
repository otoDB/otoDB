from django.utils import timezone
from datetime import timedelta

from typing import Optional, Annotated, Dict
from functools import wraps

from pydantic import field_validator

from django.contrib.contenttypes.models import ContentType

from ninja import Schema, ModelSchema, Field, Query, Router
from django_request_cache import get_request_cache

from otodb.account.models import Account
from otodb.models import (
	MediaWork,
	WorkSource,
	MediaSong,
	WorkSourceRejection,
	TagWork,
	TagWorkLangPreference,
	WikiPage,
	Pool,
	PoolItem,
	WorkRelation,
	SongRelation,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
)
from otodb.models.enums import Role, MediaType, ProfileConnectionTypes
import re


class Error(Schema):
	message: str


class ProfileSchema(ModelSchema):
	id: int

	class Meta:
		model = Account
		fields = ['username', 'level', 'date_created']


class TagWorkLangPreferenceSchema(ModelSchema):
	tag: str = Field(..., alias='tag.name')
	slug: str = Field(..., alias='tag.slug')

	class Meta:
		model = TagWorkLangPreference
		fields = ['lang']


class TagSongSchema(Schema):
	id: int
	children: list['TagSongSchema']
	name: str
	slug: str
	category: int


class SongSchema(ModelSchema):
	id: int
	work_tag: str = Field(..., alias='work_tag.slug')
	tags: list[TagSongSchema]

	class Meta:
		model = MediaSong
		fields = ['title', 'bpm', 'variable_bpm', 'author']


class TagWorkSchema(Schema):
	id: int
	lang_prefs: list[TagWorkLangPreferenceSchema]
	aliased_to: Optional['TagWorkSchema']
	n_instance: int | None = None
	name: str
	slug: str
	category: int


class FatTagWorkSchema(ModelSchema):
	id: int
	children: list[TagWorkSchema]
	song: Optional[SongSchema] = Field(None, alias='get_song')
	media_type: list[int] | None = None
	lang_prefs: list[TagWorkLangPreferenceSchema]
	aliased_to: Optional[TagWorkSchema]

	class Meta:
		model = TagWork
		fields = ['name', 'slug', 'category', 'deprecated']

	@field_validator('media_type', mode='before', check_fields=False)
	@classmethod
	def types(cls, value: int | None) -> list[int] | None:
		return [r for r in MediaType if r & value] if value else None


class WikiPageSchema(ModelSchema):
	class Meta:
		model = WikiPage
		fields = ['page_rendered', 'lang']


class TagWorkDetailsSchema(Schema):
	paths: tuple[list[TagWorkSchema], Dict[str, list[str]]]
	wiki_page: list[WikiPageSchema]
	aliases: list[TagWorkSchema]
	primary_parent: str | None = None


class WorkSourceRejectionSchema(ModelSchema):
	by: ProfileSchema

	class Meta:
		model = WorkSourceRejection
		fields = ['reason']


class WorkSourceSchema(ModelSchema):
	id: int
	added_by: ProfileSchema
	rejection: WorkSourceRejectionSchema | None = None
	thumbnail: str | None = None  # Exposed as property

	class Meta:
		model = WorkSource
		fields = [
			'platform',
			'url',
			'published_date',
			'work_width',
			'work_height',
			'work_duration',
			'title',
			'description',
			'work_origin',
			'work_status',
			'source_id',
		]


class TagWorkInstanceThinSchema(TagWorkSchema):
	sample: bool
	creator_roles: list[int] | None

	@field_validator('creator_roles', mode='before', check_fields=False)
	@classmethod
	def roles(cls, value: int | None) -> list[int] | None:
		return [r for r in Role if r & value] if value else None


class TagWorkInstanceSchema(TagWorkInstanceThinSchema):
	primary_path: list[TagWorkSchema]


class RelationSchema(Schema):
	A_id: int
	B_id: int
	relation: int


class SlimWorkSchema(ModelSchema):
	id: int
	thumbnail: str | None = None  # Exposed as property

	class Meta:
		model = MediaWork
		fields = ['title']


class WorkSchema(ModelSchema):
	id: int
	tags: list[TagWorkInstanceSchema] = Field(..., alias='tags_annotated')
	thumbnail: str | None = None  # Exposed as property
	relations: tuple[list[RelationSchema], list[SlimWorkSchema]]

	class Meta:
		model = MediaWork
		fields = ['title', 'description', 'rating', 'thumbnail_source']


class ThinWorkSchema(ModelSchema):
	id: int
	tags: list[TagWorkInstanceThinSchema] = Field(..., alias='tags_annotated')
	thumbnail: str | None = None  # Exposed as property

	class Meta:
		model = MediaWork
		fields = ['title']


class ListItemSchema(ModelSchema):
	work: ThinWorkSchema

	class Meta:
		model = PoolItem
		fields = ['description']


class ListSchema(ModelSchema):
	id: int
	author: ProfileSchema
	upstream: str | None = Field(None, alias='poolupstream')

	class Meta:
		model = Pool
		fields = ['name', 'description']

	@field_validator('upstream', mode='before', check_fields=False)
	@classmethod
	def upstream_str(cls, value) -> str:
		return value.upstream


def perm_decorator_ctor(uf):
	def decorator(f):
		@wraps(f)
		def wrapper(request, *args, **kwargs):
			if uf(request.user):
				return f(request, *args, **kwargs)
			else:
				return 403

		return wrapper

	return decorator


user_is_trusted = perm_decorator_ctor(
	lambda user: user.level > Account.Levels.RESTRICTED
)
user_is_editor = perm_decorator_ctor(lambda user: user.is_editor)
user_is_staff = perm_decorator_ctor(lambda user: user.is_staff)


def post_relation(cls, payload: RelationSchema):
	assert cls is MediaWork or cls is MediaSong
	manager = (
		cls.objects.filter(moved_to__isnull=True) if cls is MediaWork else cls.objects
	)
	rel_cls = WorkRelation if cls is MediaWork else SongRelation
	A = manager.get(id=payload.A_id)
	B = manager.get(id=payload.B_id)
	try:
		rel = rel_cls.objects.get_relation(A, B)
		rel.A = A
		rel.B = B
		rel.relation = payload.relation
		rel.save()
	except rel_cls.DoesNotExist:
		rel = rel_cls.objects.create(A=A, B=B, relation=payload.relation)
	return


class ConnectionSchema(Schema):
	site: int
	content_id: Annotated[str, Query(min_length=1)]
	dead: bool | None = None


class UserPreferencesSchema(Schema):
	language: int | None
	theme: int | None


def re_to_parser(regex):
	def matcher(link):
		m = regex.fullmatch(link)
		if m:
			return m.group(1)

	return matcher


def make_alt_value_parser(*parsers):
	def match(link):
		for v, parser in parsers:
			parse = parser(link)
			if parse:
				return (v, parse)

	return match


profile_connection_parsers = [
	(
		ProfileConnectionTypes.NICONICO,
		re_to_parser(
			re.compile(r'https?:\/\/www\.nico(?:video|log)\.jp\/user\/(\d+)\/?')
		),
	),
	(
		ProfileConnectionTypes.YOUTUBE,
		re_to_parser(
			re.compile(r'https?:\/\/www\.youtube\.com\/([^/?#]+(?:\/[^/?#]+)*)\/?')
		),
	),
	(
		ProfileConnectionTypes.BILIBILI,
		re_to_parser(re.compile(r'https?:\/\/space\.bilibili\.com\/(\d+)\/?')),
	),
	(
		ProfileConnectionTypes.TWITTER,
		re_to_parser(
			re.compile(
				r'https?:\/\/(?:twitter|x)\.com\/((?:[A-Za-z0-9_]{1,15})|(?:i\/user\/\d+))\/?'
			)
		),
	),
	(
		ProfileConnectionTypes.BLUESKY,
		re_to_parser(re.compile(r'https?:\/\/bsky\.app\/profile\/(.+?)(?:\/*)')),
	),
	(
		ProfileConnectionTypes.SOUNDCLOUD,
		re_to_parser(re.compile(r'https?:\/\/soundcloud\.com\/(.+?)(?:\/*)')),
	),
	(ProfileConnectionTypes.WEBSITE, re_to_parser(re.compile(r'(https?://.+)'))),
]


def print_queries(f):
	@wraps(f)
	def wrapper(request, *args, **kwargs):
		from django.db import connection

		r = f(request, *args, **kwargs)
		print(connection.queries)
		return r

	return wrapper


def track_revision(f):
	def get_entity_cts(model):
		return [
			ContentType.objects.get_for_model(
				model if attr == 'self' else model._meta.get_field(attr).related_model
			)
			for attr in model.revision_entity_attrs
		]

	@wraps(f)
	def wrapper(request, *args, **kwargs):
		cache = get_request_cache()
		cache.add(
			'rev', {}
		)  # key: (ContentType.pk, pk, field as str), value: (entity_pks, str)
		cache.add('rev_del', [])  # list of (ContentType.pk, pk, ...entity_pks)
		cache.add('rev_msg', '')

		ret = f(request, *args, **kwargs)

		rev = cache.get('rev')
		rev_del = cache.get('rev_del')
		rev_msg = cache.get('rev_msg')

		if len(rev) or len(rev_del):
			# Collect all affected entities from current changes
			affected_entities = set()
			for ctpk, pk, entities in rev_del:
				affected_entities.update(
					(ctpk, ent_pk) for ent_pk in entities if ent_pk
				)
			for (ctpk, pk, field), (entities, val) in rev.items():
				affected_entities.update(
					(ctpk, ent_pk) for ent_pk in entities if ent_pk
				)

			# Try to find a recent revision that:
			# - Was made within the last 60 minutes
			# - Was made by the same user
			# - Affects the exact same set of entities
			revision = None
			if affected_entities:
				five_minutes_ago = timezone.now() - timedelta(minutes=60)
				recent_revisions = (
					Revision.objects.filter(
						user=request.user, date__gte=five_minutes_ago
					)
					.prefetch_related('revisionchange_set__revisionchangeentity_set')
					.order_by('-date')
				)

				# Find a revision that affects the exact same set of entities
				for candidate_revision in recent_revisions:
					candidate_entities = set()
					for change in candidate_revision.revisionchange_set.all():
						for entity in change.revisionchangeentity_set.all():
							candidate_entities.add(
								(entity.entity_type_id, entity.entity_id)  # type: ignore
							)

					# Check if the entities match exactly
					if candidate_entities == affected_entities:
						revision = candidate_revision
						# Append new message if provided
						if rev_msg and rev_msg not in revision.message:
							revision.message = (
								revision.message
								+ ('\n' if revision.message else '')
								+ rev_msg
							)
							revision.save()
						break

			# Create new revision if no recent one found
			if revision is None:
				revision = Revision.objects.create(user=request.user, message=rev_msg)

			# For batching
			revision_changes_to_create = []
			revision_changes_to_update = []
			pending_entities = []

			# Check if we're reusing an existing revision (merging)
			merging_revision = (
				revision.pk is not None and len(revision.revisionchange_set.all()) > 0
			)

			# Process deletions
			for ctpk, pk, entities in rev_del:
				change = RevisionChange(
					rev=revision, target_type_id=ctpk, target_id=pk, deleted=True
				)
				revision_changes_to_create.append(change)
				model = ContentType.objects.get(pk=ctpk).model_class()
				pending_entities.append((change, get_entity_cts(model), entities))

			# Process updates
			for (ctpk, pk, field), (entities, val) in rev.items():
				ct = ContentType.objects.get(pk=ctpk)
				model = ct.model_class()
				target = model.objects.get(pk=pk)  # type: ignore

				# Check if this exact change already exists in the revision (only if merging)
				existing_change = None
				if merging_revision:
					existing_change = RevisionChange.objects.filter(
						rev=revision,
						target_type_id=ctpk,
						target_id=pk,
						target_column=field,
						deleted=False,
					).first()

				if existing_change:
					# Update the value instead of creating a new change
					existing_change.target_value = val
					revision_changes_to_update.append(existing_change)
				else:
					# Create new change
					change = RevisionChange(
						rev=revision,
						target=target,
						target_column=field,
						target_value=val,
					)
					revision_changes_to_create.append(change)
					pending_entities.append((change, get_entity_cts(model), entities))

			# Bulk create new changes
			if revision_changes_to_create:
				RevisionChange.objects.bulk_create(revision_changes_to_create)

			# Bulk update existing changes
			if revision_changes_to_update:
				RevisionChange.objects.bulk_update(
					revision_changes_to_update, ['target_value']
				)

			# Bulk create change entities
			revision_change_entities = []
			for change, entity_cts, entities in pending_entities:
				for entity_type, ent_pk in zip(entity_cts, entities):
					if ent_pk:
						revision_change_entities.append(
							RevisionChangeEntity(
								change=change, entity_type=entity_type, entity_id=ent_pk
							)
						)

			if revision_change_entities:
				RevisionChangeEntity.objects.bulk_create(revision_change_entities)

		return ret

	return wrapper


def add_revision_message(message: str):
	cache = get_request_cache()
	rev_msg = cache.get_or_set('rev_msg', '')
	rev_msg = rev_msg + ('\n' if rev_msg else '') + message
	cache.set('rev_msg', rev_msg)


class RouterWithRevision(Router):
	def add_api_operation(self, path, methods, view_func, **kwargs):
		view_func = track_revision(view_func)
		return super().add_api_operation(path, methods, view_func, **kwargs)
