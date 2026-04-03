from typing import Optional, Annotated, Literal
from functools import wraps, lru_cache

from pydantic import field_validator

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest

from django_request_cache import get_request_cache
from ninja import Schema, ModelSchema, Field, Query, Header, Router
from ninja.utils import contribute_operation_args
from ninja.errors import HttpError

from otodb.account.models import Account
from otodb.models import (
	MediaWork,
	WorkSource,
	MediaSong,
	Pool,
	PoolItem,
	WorkRelation,
	SongRelation,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
	Notification,
	Subscription,
)
from otodb.models.enums import (
	Role,
	ProfileConnectionTypes,
	Route,
	WorkRelationTypes,
	SongRelationTypes,
)
import re


class AuthedHttpRequest(HttpRequest):
	user: Account


class Error(Schema):
	message: str


class ProfileSchema(ModelSchema):
	id: int

	class Meta:
		model = Account
		fields = ['username', 'level', 'date_created']


class TagLangPreferenceSchema(Schema):
	tag: str = Field(..., alias='tag.name')
	slug: str = Field(..., alias='tag.slug')
	lang: int


class TagWorkSchema(Schema):
	id: int
	lang_prefs: list[TagLangPreferenceSchema]
	aliased_to: Optional['TagWorkSchema']
	n_instance: int | None = None
	name: str
	slug: str
	category: int
	deprecated: bool


class ConnectionTagResult(TagWorkSchema):
	has_connection: bool


class ConnectionLookupResponse(Schema):
	entities: list[ConnectionTagResult]


class WorkSourceSchema(ModelSchema):
	id: int
	added_by: ProfileSchema
	thumbnail: str | None = None  # Exposed as property
	media_title: str | None = None

	@staticmethod
	def resolve_media_title(obj):
		return obj.media.title if obj.media else None

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
			'uploader_id',
			'media',
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
	tags: list[TagWorkInstanceThinSchema] = Field(..., alias='tags_annotated_thin')
	thumbnail: str | None = None  # Exposed as property

	class Meta:
		model = MediaWork
		fields = ['title']


class SourceCreationResponse(Schema):
	source_id: int | None = None
	work_id: int | None = None


class TagWorkInstanceInSchema(Schema):
	nameslug: str
	sample: bool | None = None
	roles: list[Annotated[int, Field(ge=1, le=max(Role.values))]] | None = None


class CreateWorkPayload(Schema):
	source_id: int
	title: str | None = None
	description: str | None = None
	rating: int = 0
	tags: list[TagWorkInstanceInSchema] = []


class SourceSuggestionsResponse(Schema):
	title: str | None = None
	description: str | None = None
	source_tags: list[TagWorkSchema] = []
	new_tags: list[TagWorkSchema] = []
	creator_tags: list[TagWorkSchema] = []


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
				raise HttpError(403, 'Forbidden')

		return wrapper

	return decorator


user_is_trusted = perm_decorator_ctor(
	lambda user: user.level > Account.Levels.RESTRICTED
)
user_is_editor = perm_decorator_ctor(lambda user: user.is_editor)
user_is_staff = perm_decorator_ctor(lambda user: user.is_staff)


def post_relations(cls, obj_id: int, payload: list[RelationSchema]):
	assert cls is MediaWork or cls is MediaSong
	assert all(rel.A_id == obj_id or rel.B_id == obj_id for rel in payload)

	rel_cls, rt_cls = (
		(WorkRelation, WorkRelationTypes)
		if cls is MediaWork
		else (SongRelation, SongRelationTypes)
	)
	old_As, old_Bs = (
		rel_cls.objects.filter(A_id=obj_id),
		rel_cls.objects.filter(B_id=obj_id),
	)
	new_As_B, new_Bs_A = (
		[rel.B_id for rel in payload if rel.A_id == obj_id],
		[rel.A_id for rel in payload if rel.B_id == obj_id],
	)

	old_As.exclude(B_id__in=new_As_B).delete()
	old_Bs.exclude(A_id__in=new_Bs_A).delete()

	if cls is MediaWork:
		assert not cls.objects.filter(
			id__in=new_As_B + new_Bs_A,
			moved_to__isnull=False,
		).exists()

	for rel in payload:
		rel_cls.objects.update_or_create(
			A_id=rel.A_id,
			B_id=rel.B_id,
			defaults={'relation': rt_cls(rel.relation).value},
		)


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


@lru_cache(maxsize=128)
def _get_entity_cts(model):
	return [
		ContentType.objects.get_for_model(
			model if attr == 'self' else model._meta.get_field(attr).related_model
		)
		for attr in model._revision_meta.entity_attrs
	]


def track_revision(f):
	@wraps(f)
	def wrapper(request, *args, **kwargs):
		cache = get_request_cache()
		cache.add(
			'rev', {}
		)  # key: (ContentType.pk, pk, field as str), value: (entity_pks, str)
		cache.add('rev_del', [])  # list of (ContentType.pk, pk, ...entity_pks)
		cache.add('rev_rst', {})
		cache.add('rev_msg', '')

		ret = f(request, *args, **kwargs)

		rev = cache.get('rev')
		rev_del = cache.get('rev_del')
		rev_msg = cache.get('rev_msg')
		rev_rst = cache.get('rev_rst')
		# REVIEW: This should never be unknown but some test cases might not set it; should fix those tests
		rev_route = cache.get('rev_route', Route.UNKNOWN)

		if len(rev) or len(rev_del) or len(rev_rst):
			revision = Revision.objects.create(user=request.user, message=rev_msg)

			# Pre-fetch all ContentTypes in bulk
			content_types = ContentType.objects.in_bulk(
				set(ctpk for ctpk, *_ in rev_del)
				| set(ctpk for (ctpk, *_), _ in rev.items())
			)

			# For batching
			revision_changes = []
			pending_entities = []
			subscribers = []

			# Process deletions
			seen_deletions = {}
			for ctpk, pk, entities in rev_del:
				key = (ctpk, pk)
				if key not in seen_deletions:
					seen_deletions[key] = entities
					change = RevisionChange(
						rev=revision, target_type_id=ctpk, target_id=pk, deleted=True
					)
					revision_changes.append(change)
					model = content_types[ctpk].model_class()
					pending_entities.append((change, _get_entity_cts(model), entities))

					subs = Subscription.objects.filter(
						entity_type_id=ctpk, entity_id=pk
					)
					subscribers.extend(subs.values_list('subscriber_id', flat=True))
					subs.delete()

			# Process updates
			for (ctpk, pk, field), (entities, val) in rev.items():
				ct = content_types[ctpk]
				model = ct.model_class()
				change = RevisionChange(
					rev=revision,
					target_type_id=ctpk,
					target_id=pk,
					target_column=field,
					target_value=val,
				)
				revision_changes.append(change)
				pending_entities.append((change, _get_entity_cts(model), entities))
				subs = Subscription.objects.filter(entity_type_id=ctpk, entity_id=pk)
				subscribers.extend(subs.values_list('subscriber_id', flat=True))
				subs.delete()

			for (ctpk, pk), to_pk in rev_rst.items():
				revision_changes.append(
					RevisionChange(
						rev=revision,
						target_type_id=ctpk,
						target_id=pk,
						target_value=to_pk,
						restored=True,
					)
				)

			# Bulk create changes
			RevisionChange.objects.bulk_create(revision_changes)

			# Bulk create change entities
			revision_change_entities = []
			subscriptions = []
			for change, entity_cts, entities in pending_entities:
				for entity_type, ent_pk in zip(entity_cts, entities):
					if ent_pk:
						# TODO: add if rev_route == ROLLBACK OR better probably should move this to rollback_entity
						from .history import get_rev_restored

						ent_pk = get_rev_restored(entity_type.id, ent_pk) or ent_pk
						revision_change_entities.append(
							RevisionChangeEntity(
								change=change,
								entity_type=entity_type,
								entity_id=ent_pk,
								route=rev_route,
							)
						)
						subscriptions.append(
							Subscription(
								subscriber=request.user,
								entity_type=entity_type,
								entity_id=ent_pk,
							)
						)

			if revision_change_entities or subscriptions:
				RevisionChangeEntity.objects.bulk_create(revision_change_entities)
				Subscription.objects.bulk_create(subscriptions, ignore_conflicts=True)
			Notification.objects.bulk_create(
				[
					Notification(revision=revision, target_id=sub)
					for sub in set(subscribers)
					if sub != request.user.id
				]
			)

		return ret

	return wrapper


def add_revision_message(message: str):
	cache = get_request_cache()
	rev_msg = cache.get_or_set('rev_msg', '')
	rev_msg = rev_msg + ('\n' if rev_msg else '') + message
	cache.set('rev_msg', rev_msg)


def with_revision_route(route: Route):
	"""Decorator to set the revision route for a API endpoint."""

	def decorator(f):
		@wraps(f)
		def wrapper(request, *args, **kwargs):
			cache = get_request_cache()
			cache.set('rev_route', route.value)
			return f(request, *args, **kwargs)

		return wrapper

	return decorator


class RouterWithRevision(Router):
	def add_api_operation(self, path, methods, view_func, **kwargs):
		view_func = track_revision(view_func)
		return super().add_api_operation(path, methods, view_func, **kwargs)


def restrict_internal(f):
	@wraps(f)
	def wrapper(request, *args, **kwargs):
		secret = kwargs.pop('otodb-internal-secret')
		if secret == settings.OTODB_INTERNAL_API_SECRET:
			return f(request, *args, **kwargs)
		else:
			raise HttpError(403, 'Forbidden')

	contribute_operation_args(wrapper, 'otodb-internal-secret', str, Header(...))

	return wrapper


class EntitySchema(Schema):
	id: int | str
	entity: Literal['mediawork', 'tagwork', 'tagsong', 'mediasong', 'worksource', 'revision']
