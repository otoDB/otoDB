import operator
import re
from functools import lru_cache, reduce, wraps
from typing import Annotated, Any, Callable, NamedTuple, Optional, Self

import lark
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Exists, OuterRef, Q
from django.http import HttpRequest
from django_request_cache import get_request_cache
from ninja import Field, Header, ModelSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.utils import contribute_operation_args
from pydantic import create_model, field_validator, model_validator

from otodb.account.models import Account
from otodb.common import slugify_tag
from otodb.models import (
	MediaSong,
	MediaWork,
	ModerationEvent,
	Notification,
	Pool,
	PoolItem,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
	SongRelation,
	Subscription,
	WorkRelation,
	WorkSource,
)
from otodb.models.enums import (
	ErrorCode,
	FlagStatus,
	LanguageTypes,
	Platform,
	Preferences,
	PreferencesValueTypeMap,
	ProfileConnectionTypes,
	Rating,
	Role,
	Route,
	SongRelationTypes,
	Status,
	WorkOrigin,
	WorkRelationTypes,
	WorkStatus,
	WorkTagCategory,
)
from otodb.models.tag import OtodbTagModel


class AuthedHttpRequest(HttpRequest):
	user: Account


class Error(Schema):
	code: ErrorCode
	data: dict | None = None


class ProfileSchema(ModelSchema):
	id: int
	level: Account.Levels

	class Meta:
		model = Account
		fields = ['username', 'date_created']


class TagLangPreferenceSchema(Schema):
	tag: str = Field(..., alias='tag.name')
	slug: str = Field(..., alias='tag.slug')
	lang: LanguageTypes = Field(..., gt=0)


class TagWorkSchema(Schema):
	id: int
	lang_prefs: list[TagLangPreferenceSchema]
	aliased_to: Optional['TagWorkSchema']
	name: str
	slug: str
	category: WorkTagCategory
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
	platform: Platform
	work_origin: WorkOrigin
	work_status: WorkStatus

	@staticmethod
	def resolve_media_title(obj):
		return obj.media.title if obj.media else None

	class Meta:
		model = WorkSource
		fields = [
			'url',
			'published_date',
			'work_width',
			'work_height',
			'work_duration',
			'title',
			'description',
			'source_id',
			'uploader_id',
			'is_pending',
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


class WorkRelationSchema(RelationSchema):
	relation: WorkRelationTypes


class SongRelationSchema(RelationSchema):
	relation: SongRelationTypes


class SlimWorkSchema(ModelSchema):
	id: int
	thumbnail: str | None = None  # Exposed as property
	status: Status

	class Meta:
		model = MediaWork
		fields = ['title']


class WorkSchema(ModelSchema):
	id: int
	tags: list[TagWorkInstanceSchema] = Field(..., alias='tags_annotated')
	thumbnail: str | None = None  # Exposed as property
	pending_flag: 'PendingModerationEventSchema | None' = None
	pending_appeal: 'PendingModerationEventSchema | None' = None
	relations: tuple[list[WorkRelationSchema], list[SlimWorkSchema]]
	rating: Rating
	status: Status

	class Meta:
		model = MediaWork
		fields = ['title', 'description', 'thumbnail_source']


class ThinWorkSchema(ModelSchema):
	id: int
	tags: list[TagWorkInstanceThinSchema] = Field(..., alias='tags_annotated_thin')
	thumbnail: str | None = None  # Exposed as property
	pending_flag: 'PendingModerationEventSchema | None' = None
	pending_appeal: 'PendingModerationEventSchema | None' = None
	status: Status

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
	rating: Rating = Rating.GENERAL
	tags: list[TagWorkInstanceInSchema] = []


class SourceSuggestionsResponse(Schema):
	title: str | None = None
	description: str | None = None
	source_tags: list[TagWorkSchema] = []
	new_tags: list[TagWorkSchema] = []
	creator_tags: list[TagWorkSchema] = []


class PendingModerationEventSchema(ModelSchema):
	"""Thin view of a pending flag or appeal exposed on a work."""

	id: int
	by: ProfileSchema | None = None
	status: FlagStatus

	class Meta:
		model = ModerationEvent
		fields = ['reason', 'date']


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


class ApiError(Exception):
	def __init__(self, status: int, code: ErrorCode, data: dict | None = None) -> None:
		super().__init__(code.name)
		self.status = status
		self.code = code
		self.data = data


def ensure_can_moderate(user: Account, work: MediaWork | None) -> None:
	"""Block non-staff moderators from resolving a work they contributed to."""
	if user.is_staff:
		return
	if work is not None and work.was_contributed_by(user):
		raise ApiError(403, ErrorCode.SELF_MODERATION)


def post_relations(cls, obj_id: int, payload: list[RelationSchema]):
	assert cls is MediaWork or cls is MediaSong
	assert all(rel.A_id == obj_id or rel.B_id == obj_id for rel in payload)

	rel_cls, _rt_cls = (
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
			defaults={'relation': rel.relation},
		)


class ConnectionSchema(Schema):
	site: int
	content_id: Annotated[str, Query(min_length=1)]
	dead: bool | None = None


@model_validator(mode='after')
def _UserPreferenceSchema_verify_value(self) -> Self:
	disallowed_values = {
		Preferences.LANGUAGE: [LanguageTypes.NOT_APPLICABLE],
	}
	for setting, value in self.dict().items():
		if value is not None:
			setting = getattr(Preferences, setting)
			v = PreferencesValueTypeMap[setting](value)
			if setting in disallowed_values:
				assert v not in disallowed_values[setting]
			setattr(self, setting.name, v)
	return self


UserPreferenceSchema = create_model(
	'UserPreferenceSchema',
	__base__=Schema,
	__validators__={'verify_value': _UserPreferenceSchema_verify_value},
	**{
		name: (PreferencesValueTypeMap[value], None)
		for name, value in zip(Preferences.names, Preferences.values)
	},
)


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
		if secret == settings.INTERNAL_API_SECRET:
			return f(request, *args, **kwargs)
		else:
			raise HttpError(403, 'Forbidden')

	contribute_operation_args(wrapper, 'otodb-internal-secret', str, Header(...))

	return wrapper


class MetatagSpec(NamedTuple):
	kind: Any
	to_q: Callable


def get_search_grammar(metatag_grammars: dict[str, MetatagSpec]):
	def metatag_rule(name: str, spec: MetatagSpec):
		value_rule = 'range_value' if spec.kind is int else f'{name.upper()}_VALUE'
		return f'{name}_meta: "{name}"i _META_CONN {value_rule}'

	enum_value_terminals = '\n'.join(
		f'{k.upper()}_VALUE: /{"|".join(spec.kind.names)}/i'
		for k, spec in metatag_grammars.items()
		if spec.kind is not int
	)

	return lark.Lark(rf"""
start: or_expr?
or_expr: and_expr (_OR and_expr)*
and_expr: atom+
atom: MODIFIERS? (tag_part | metatag_part | _LPAR or_expr _RPAR)

tag_part: TAG_MODIFIERS? SLUG

range_value: COMPARATOR INT     -> range_compare
           | INT ".." INT       -> range_between
           | INT ".."           -> range_min
           | ".." INT           -> range_max
           | INT                -> range_eq

MODIFIERS:     /[-]/
TAG_MODIFIERS: /[\^]/
SLUG:          /\w+/u
COMPARATOR:    ">=" | "<=" | ">" | "<"
INT:           /\d+/
_LPAR: "("
_RPAR: ")"
_OR: "|"
{'\n'.join(metatag_rule(k, spec) for k, spec in metatag_grammars.items())}
{enum_value_terminals}
metatag_part: {'|'.join([k + '_meta' for k in metatag_grammars])}
_META_CONN: ":"

%import common.WS
%ignore WS
""")


def _parse_range_node(node):
	match node.data, node.children:
		case 'range_eq', (v,):
			return 'exact', int(v)
		case 'range_compare', ('>', v):
			return 'gt', int(v)
		case 'range_compare', ('>=', v):
			return 'gte', int(v)
		case 'range_compare', ('<', v):
			return 'lt', int(v)
		case 'range_compare', ('<=', v):
			return 'lte', int(v)
		case 'range_between', (lo, hi):
			return 'range', (int(lo), int(hi))
		case 'range_min', (v,):
			return 'gte', int(v)
		case 'range_max', (v,):
			return 'lte', int(v)
		case _:
			raise ValueError(
				f'unrecognized range_value: {node.data!r}/{node.children!r}'
			)


def make_range_metatag(
	field=None, *, model=None, fk_field=None, count=False, **filters
):
	if count:

		def count_q(op, value):
			base = model.objects.filter(**{fk_field: OuterRef('id')}, **filters)
			grouped = base.values(fk_field).annotate(c=Count('*'))
			positive = Exists(grouped.filter(**{f'c__{op}': value}))
			zero_matches = (
				op == 'lte'
				or (op in ('exact', 'gte') and value == 0)
				or (op == 'lt' and value > 0)
				or (op == 'range' and value[0] == 0)
			)
			return positive | ~Exists(base) if zero_matches else positive

		return count_q

	if model is not None:
		return lambda op, value: Exists(
			model.objects.filter(
				**{fk_field: OuterRef('id'), f'{field}__{op}': value}, **filters
			)
		)

	return lambda op, value: Q(**{f'{field}__{op}': value})


class AbstractTagTransformer(lark.Transformer):
	TagModel: OtodbTagModel
	tag_join_name: str
	tagged_join_name: str
	metatag_grammars: dict

	def start(self, v):
		return v[0] if v else None

	def or_expr(self, v):
		return v[0] if len(v) == 1 else reduce(operator.or_, v)

	def and_expr(self, v):
		return v[0] if len(v) == 1 else reduce(operator.and_, v)

	def atom(self, v):
		if len(v) == 1:
			return v[0]
		elif v[0] == '-':
			return ~v[1]

	MODIFIERS = str
	TAG_MODIFIERS = str

	def SLUG(self, v):
		return str(v)

	def tag_part(self, v):
		slug = v[0] if len(v) == 1 else v[1]
		try:
			tag = self.TagModel.objects.get(slug=slugify_tag(slug))
		except self.TagModel.DoesNotExist:
			return Q(pk__in=[])
		if tag.aliased_to:
			tag = tag.aliased_to
		twi_q = self.TagInstanceModel.objects.filter(
			**{self.tagged_join_name: OuterRef('id')}
		)

		if len(v) == 1:
			ids = [tag.id, *tag.get_descendants().values_list('id', flat=True)]
			return Exists(twi_q.filter(**{f'{self.tag_join_name}__in': ids}))
		elif v[0] == '^':
			return Exists(twi_q.filter(**{self.tag_join_name: tag}))

	def metatag_part(self, v):
		v = v[0]
		metatag = v.data.value[:-5]
		spec = self.metatag_grammars[metatag]
		if spec.kind is int:
			op, value = _parse_range_node(v.children[0])
			return spec.to_q(op, value)
		E = spec.kind
		return spec.to_q(E(E.names.index(str(v.children[0]).upper())))
