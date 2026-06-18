import functools
import logging
from datetime import date, datetime
from enum import Enum
from itertools import groupby
from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import connection, models, transaction
from django.db.models import Case, Count, Exists, F, OuterRef, Q, Subquery, When, Window
from django.db.models.fields.related import RelatedField
from django.db.models.functions import Coalesce, RowNumber
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django_cte import CTE, with_cte
from django_request_cache import get_request_cache
from fast_diff_match_patch import diff
from ninja import Field, ModelSchema, Query, Router, Schema
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.account.models import Account
from otodb.common import slugify_tag
from otodb.models import (
	MediaSong,
	MediaWork,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
	TagSong,
	TagWork,
	TagWorkInstance,
	WikiPage,
	WorkSource,
)
from otodb.models.enums import RevisionChain, Route
from otodb.models.revision import RevisionTrackedModel
from otodb.models.tag import OtodbTagModel

from .common import (
	OtodbID,
	SlimWorkSchema,
	add_revision_message,
	track_revision,
	user_is_mod,
	with_revision_route,
)

history_router = Router()

logger = logging.getLogger(__name__)


@functools.cache
def _wikipage_ct_id() -> int:
	return ContentType.objects.get_for_model(WikiPage).id


@functools.cache
def _slug_model_ids() -> tuple[int, ...]:
	return tuple(
		[ContentType.objects.get_for_model(WikiPage).id]
		+ [
			ct.id
			for ct in ContentType.objects.get_for_models(
				*OtodbTagModel.__subclasses__()
			).values()
		]
	)


class HistoricalEntities(str, Enum):
	WORK = 'mediawork'
	TAG = 'tagwork'
	SONG_ATTRIBUTE = 'tagsong'
	SONG = 'mediasong'
	UPLOAD = 'worksource'
	WIKI = 'wikipage'


class EntityModels(str, Enum):
	WORK = 'mediawork'
	SONG = 'mediasong'
	TAG = 'tagwork'
	SONG_ATTRIBUTE = 'tagsong'
	UPLOAD = 'worksource'
	PROFILE = 'account'
	LIST = 'pool'
	REQUEST = 'bulkrequest'
	WIKI = 'wikipage'
	POST = 'post'


class HistoricalEntitySchema(Schema):
	id: str
	entity: HistoricalEntities


class RevisionSchema(ModelSchema):
	id: OtodbID
	date: datetime
	user: str = Field(..., alias='user.username')
	index: None | int = None
	route: None | Route = None

	class Meta:
		model = Revision
		fields = ['message']


class RevisionEntitySummarySchema(RevisionSchema):
	first_entity: HistoricalEntitySchema | None = None
	n_ent: int

	@staticmethod
	def resolve_first_entity(obj) -> dict | None:
		if obj.first_ent_type is None:
			return None
		return {'id': obj.first_ent, 'entity': obj.first_ent_type}


class OldColumnSchema(Schema):
	column: str
	value: str | None = None
	# Related model when the column is a foreign key
	ref: EntityModels | None = None


class DiffSegmentSchema(Schema):
	# diff-match-patch op:
	# -1 delete, 0 equal, 1 insert
	# custom op:
	# 2 collapsed unchanged region
	op: int
	text: str


_DIFF_MIN_LENGTH = 255

# Collapse long unchanged runs to a window of context around each change, so
# minor edits aren't buried in the middle of a large field.
_DIFF_OP_GAP = 2
# Characters of unchanged context to keep on each side of a change.
_DIFF_CONTEXT = 80
# Don't collapse unless it actually hides a meaningful chunk.
_DIFF_MIN_GAP = 40
# Snap a cut to a nearby line boundary, but only if it's close.
_DIFF_SNAP = 200

_DIFF_OP_CODES = {'-': -1, '=': 0, '+': 1}


def _head_context(text: str, keep: int) -> int:
	"""End index keeping the first `keep` chars, extended to the line's end."""
	end = min(len(text), keep)
	nl = text.find('\n', end)
	if nl != -1 and nl - end <= _DIFF_SNAP:
		end = nl
	return end


def _tail_context(text: str, keep: int) -> int:
	"""Start index keeping the last `keep` chars, extended to the line's start."""
	start = max(0, len(text) - keep)
	if start > 0:
		nl = text.rfind('\n', 0, start + 1)
		if nl != -1 and start - nl <= _DIFF_SNAP:
			start = nl + 1
	return start


def _window_diff(diffs: list[tuple[int, str]]) -> list[DiffSegmentSchema]:
	n = len(diffs)
	out: list[DiffSegmentSchema] = []
	for i, (op, text) in enumerate(diffs):
		has_before = i > 0
		has_after = i < n - 1
		keep = (_DIFF_CONTEXT if has_before else 0) + (
			_DIFF_CONTEXT if has_after else 0
		)
		if op != 0 or len(text) - keep < _DIFF_MIN_GAP:
			out.append(DiffSegmentSchema(op=op, text=text))
			continue
		head_end = _head_context(text, _DIFF_CONTEXT) if has_before else 0
		tail_start = _tail_context(text, _DIFF_CONTEXT) if has_after else len(text)
		if tail_start - head_end < _DIFF_MIN_GAP:
			out.append(DiffSegmentSchema(op=op, text=text))
			continue
		if has_before:
			out.append(DiffSegmentSchema(op=0, text=text[:head_end]))
		out.append(DiffSegmentSchema(op=_DIFF_OP_GAP, text=text[head_end:tail_start]))
		if has_after:
			out.append(DiffSegmentSchema(op=0, text=text[tail_start:]))
	return out


# Models whose rows are displayed as a whole (all columns) rather than per-column
_CONTEXT_MODELS = ('workrelation', 'songrelation', 'tagworkparenthood')


class RevisionChangeSchema(ModelSchema):
	target_type: str = Field(..., alias='target_type.model')
	target_id: OtodbID
	ent_type: str
	ent_id: str
	route: Route
	tg_id: str
	old_value: str | None = None
	created: bool
	# Related model when target_column is a foreign key
	ref: EntityModels | None = None
	diff: list[DiffSegmentSchema] | None = None

	class Meta:
		model = RevisionChange
		fields = ['deleted', 'restored', 'target_column', 'target_value']

	@staticmethod
	def resolve_ref(obj) -> EntityModels | None:
		model = REVISION_FK_COLUMNS()[obj.target_type_id].get(obj.target_column)
		if model is None:
			return None
		try:
			return EntityModels(model._meta.model_name)
		except ValueError:
			return None

	@staticmethod
	def resolve_diff(obj) -> list[DiffSegmentSchema] | None:
		cols = REVISION_TEXT_COLUMNS().get(obj.target_type_id)
		if not cols or obj.target_column not in cols:
			return None
		old, new = obj.old_value, obj.target_value
		if not isinstance(old, str) or not isinstance(new, str):
			return None
		if len(old) <= _DIFF_MIN_LENGTH:
			return None
		try:
			raw = diff(old, new, counts_only=False, cleanup='Semantic', timelimit=1)
		except ValueError, RuntimeError:
			# Windows moment
			# https://github.com/JoshData/fast_diff_match_patch#:~:text=On%20Windows
			return None
		diffs = [(_DIFF_OP_CODES[op], text) for op, text in raw]
		return _window_diff(diffs)


class RevisionDetailsSchema(Schema):
	changes: list[RevisionChangeSchema]
	works: list[SlimWorkSchema]
	# "model:id" -> display label (e.g. tag slug, song title) for non-work FK refs
	labels: dict[str, str]
	# "model:id" -> last known column values of rows deleted in this revision
	deleted_rows: dict[str, list[OldColumnSchema]]
	# "model:id" -> current column values of rows touched by this revision, for
	# rows whose identity lives in FK columns (a change to only one column would
	# otherwise lose the context of what the row connects)
	row_context: dict[str, list[OldColumnSchema]]


@history_router.get('recent', response=list[RevisionEntitySummarySchema])
@paginate
def recent(request: HttpRequest, username: str | None = None):
	rce_subq = RevisionChangeEntity.objects.filter(change__rev=OuterRef('id')).order_by(
		'id'
	)
	q = (
		Revision.objects.select_related('user')
		.annotate(
			route=Subquery(rce_subq.values('route')[:1]),
			n_ent=Coalesce(
				Subquery(
					rce_subq.order_by()
					.values('change__rev')
					.annotate(
						c=Count(
							models.functions.Concat(
								models.functions.Cast(
									'entity_type_id', output_field=models.CharField()
								),
								models.Value('-'),
								models.functions.Cast(
									'entity_id', output_field=models.CharField()
								),
							),
							distinct=True,
						)
					)
					.values('c')[:1]
				),
				0,
			),
			first_ent_id=Subquery(rce_subq.values('entity_id')[:1]),
			first_ent_type=Subquery(rce_subq.values('entity_type__model')[:1]),
			first_ent_type_id=Subquery(rce_subq.values('entity_type_id')[:1]),
		)
		.annotate(
			first_ent=Case(
				When(
					Q(first_ent_type_id__in=_slug_model_ids()),
					# Fall back to the numeric id when no slug change was recorded
					then=Coalesce(
						Subquery(
							RevisionChange.objects.filter(
								target_type_id=OuterRef('first_ent_type_id'),
								target_id=OuterRef('first_ent_id'),
								target_column='slug',
							)
							.order_by('-rev_id')
							.values('target_value')[:1]
						),
						models.functions.Cast(
							F('first_ent_id'),
							output_field=models.TextField(),
						),
					),
				),
				default=models.functions.Cast(
					F('first_ent_id'),
					output_field=models.TextField(),
				),
				output_field=models.TextField(),
			)
		)
		.order_by('-id')
	)
	if username:
		q = q.filter(user__username=username)
	return q


@history_router.get('revision', response=RevisionSchema)
def revision(request: HttpRequest, revision_id: OtodbID):
	return get_object_or_404(Revision, id=revision_id)


@functools.cache
def REVISION_FK_COLUMNS() -> dict[int, dict[str, Any]]:
	return {
		ContentType.objects.get_for_model(c).id: {
			f: c._meta.get_field(f).related_model
			for f in c._revision_meta.tracked_fields
			if isinstance(c._meta.get_field(f), RelatedField)
		}
		for c in RevisionTrackedModel.__subclasses__()
	}


@functools.cache
def REVISION_TEXT_COLUMNS() -> dict[int, set[str]]:
	return {
		ContentType.objects.get_for_model(c).id: {
			f
			for f in c._revision_meta.tracked_fields
			if isinstance(c._meta.get_field(f), (models.CharField, models.TextField))
		}
		for c in RevisionTrackedModel.__subclasses__()
	}


# The most recent value the target column held before this change's revision.
_old_value_subquery = Subquery(
	RevisionChange.objects.filter(
		target_type_id=OuterRef('target_type_id'),
		target_id=OuterRef('target_id'),
		target_column=OuterRef('target_column'),
		rev_id__lt=OuterRef('rev_id'),
	)
	.order_by('-rev_id')
	.values('target_value')[:1]
)


def _label_field(model_class) -> str | None:
	field_names = {f.name for f in model_class._meta.fields}
	if 'slug' in field_names:
		return 'slug'
	if 'username' in field_names:
		return 'username'
	if 'title' in field_names:
		return 'title'
	return None


def _historic_labels(model_class, ids: set[int], label_field: str) -> dict[int, str]:
	"""Last recorded label values for rows that no longer exist in the live table."""
	return dict(
		RevisionChange.objects.filter(
			target_type=ContentType.objects.get_for_model(model_class),
			target_id__in=ids,
			target_column=label_field,
		)
		.order_by('target_id', '-rev_id')
		.distinct('target_id')
		.values_list('target_id', 'target_value')
	)


@history_router.get('revision_changes', response=RevisionDetailsSchema)
def revision_changes(request: HttpRequest, revision_id: OtodbID):
	rev = get_object_or_404(Revision, id=revision_id)

	# TODO: Don't display 1st revision changes with a ton of objects for now.
	# Should revisit to remove the need for this constraint.
	is_first = not Revision.objects.filter(pk__lt=rev.pk).exists()
	if is_first and RevisionChange.objects.filter(rev=rev).count() > 50_000:
		return RevisionDetailsSchema(
			changes=[],
			works=[],
			labels={},
			deleted_rows={},
			row_context={},
		)

	qq = (
		RevisionChange.objects.filter(rev=rev)
		.filter(revisionchangeentity__isnull=False)
		.select_related('target_type')
		.annotate(
			ent_id=(
				Case(
					When(
						# Wikipage slugs live on the row, not in slug-column history
						Q(revisionchangeentity__entity_type_id=_wikipage_ct_id()),
						then=Coalesce(
							Subquery(
								WikiPage.objects.filter(
									pk=OuterRef('revisionchangeentity__entity_id')
								).values('slug')[:1]
							),
							models.functions.Cast(
								F('revisionchangeentity__entity_id'),
								output_field=models.TextField(),
							),
						),
					),
					When(
						Q(revisionchangeentity__entity_type__id__in=_slug_model_ids()),
						# Fall back to the numeric id when no slug change was recorded
						then=Coalesce(
							Subquery(
								RevisionChange.objects.filter(
									target_type_id=OuterRef(
										'revisionchangeentity__entity_type_id'
									),
									target_id=OuterRef(
										'revisionchangeentity__entity_id'
									),
									target_column='slug',
								)
								.order_by('-rev_id')
								.values('target_value')[:1]
							),
							models.functions.Cast(
								F('revisionchangeentity__entity_id'),
								output_field=models.TextField(),
							),
						),
					),
					default=models.functions.Cast(
						F('revisionchangeentity__entity_id'),
						output_field=models.TextField(),
					),
					output_field=models.TextField(),
				)
			),
			tg_id=(
				Case(
					When(
						# Wikipage slugs live on the row, not in slug-column history
						Q(target_type_id=_wikipage_ct_id()),
						then=Coalesce(
							Subquery(
								WikiPage.objects.filter(
									pk=OuterRef('target_id')
								).values('slug')[:1]
							),
							models.functions.Cast(
								F('target_id'), output_field=models.TextField()
							),
						),
					),
					When(
						Q(target_type__id__in=_slug_model_ids()),
						# Fall back to the numeric id when no slug change was recorded
						then=Coalesce(
							Subquery(
								RevisionChange.objects.filter(
									target_type_id=OuterRef('target_type_id'),
									target_id=OuterRef('target_id'),
									target_column='slug',
								)
								.order_by('-rev_id')
								.values('target_value')[:1]
							),
							models.functions.Cast(
								F('target_id'), output_field=models.TextField()
							),
						),
					),
					default=models.functions.Cast(
						F('target_id'), output_field=models.TextField()
					),
					output_field=models.TextField(),
				)
			),
			ent_type=F('revisionchangeentity__entity_type__model'),
			route=F('revisionchangeentity__route'),
			old_value=_old_value_subquery,
			# No prior change for the row at all ~= row created in this revision
			created=~Exists(
				RevisionChange.objects.filter(
					target_type_id=OuterRef('target_type_id'),
					target_id=OuterRef('target_id'),
					rev_id__lt=OuterRef('rev_id'),
				)
			),
		)
		.order_by('id')
	)
	qq_list = list(qq)

	# A wikipage change is shown as its own top-level "self" group (by slug), and
	# also under any tag/work it belongs to. Once it belongs to a tag/work, the
	# self group is redundant, so drop it and let the wiki nest under the tag/work.
	# A bare wiki page (grouped under nothing else) keeps its top-level group.
	ids_under_tag_or_work = {c.id for c in qq_list if c.ent_type != 'wikipage'}
	qq_list = [
		c
		for c in qq_list
		if not (c.ent_type == 'wikipage' and c.id in ids_under_tag_or_work)
	]

	"""
	Resolve everything a revision's changes reference, for display purposes:
	works referenced by FK columns (as card data), labels for other FK refs,
	and the last known values of rows deleted in the revision.
	"""
	changes = RevisionChange.objects.filter(rev=rev)

	content_types = ContentType.objects.in_bulk(
		set(changes.values_list('target_type_id', flat=True).distinct())
	)
	fk_columns = {ct_id: REVISION_FK_COLUMNS()[ct_id] for ct_id in content_types}

	col_order = {
		ct.model: {
			field: index
			for index, field in enumerate(
				getattr(
					getattr(ct.model_class(), '_revision_meta', None),
					'tracked_fields',
					[],
				)
			)
		}
		for ct in content_types.values()
	}

	ref_ids: dict[str, set[int]] = {}

	def collect_ref(model_class, value) -> EntityModels | None:
		name = model_class._meta.model_name
		if name and value is not None:
			try:
				ref_ids.setdefault(name, set()).add(int(value))
			except ValueError:
				pass
		try:
			return EntityModels(name) if name else None
		except ValueError:
			return None

	# Collect new and previous ids from changes to FK columns
	for c in qq_list:
		ref_model = fk_columns.get(c.target_type_id, {}).get(c.target_column)
		if ref_model is not None:
			collect_ref(ref_model, c.target_value)
			collect_ref(ref_model, c.old_value)

	def reconstruct_rows(
		targets: models.QuerySet, **rev_filter
	) -> dict[str, list[OldColumnSchema]]:
		"""Latest known value per column for each (target_type, target_id) row."""
		rows: dict[str, list[OldColumnSchema]] = {}
		member = targets.filter(
			target_type_id=OuterRef('target_type_id'),
			target_id=OuterRef('target_id'),
		)
		latest = (
			RevisionChange.objects.filter(
				Exists(member), target_column__isnull=False, **rev_filter
			)
			.order_by('target_type_id', 'target_id', 'target_column', '-rev_id')
			.distinct('target_type_id', 'target_id', 'target_column')
			.values_list('target_type_id', 'target_id', 'target_column', 'target_value')
		)
		for tt, tid, column, value in latest:
			rm = fk_columns.get(tt, {}).get(column)
			rows.setdefault(f'{content_types[tt].model}:{tid}', []).append(
				OldColumnSchema(
					column=column,
					value=value,
					ref=collect_ref(rm, value) if rm else None,
				)
			)
		# Re-order each row's columns to match the model's declared field order
		for key, cols in rows.items():
			order = col_order.get(key.rsplit(':', 1)[0], {})
			cols.sort(key=lambda c: order.get(c.column, len(order)))
		return rows

	# Reconstruct the last known column values of rows deleted in this revision
	deleted_rows = reconstruct_rows(
		changes.filter(deleted=True),
		rev_id__lt=rev.pk,
	)

	# Full-row context for relation-like rows: a change to only some columns
	# would otherwise lose what the row connects (e.g. relation type-only edits)
	row_context = reconstruct_rows(
		changes.filter(deleted=False, target_type__model__in=_CONTEXT_MODELS),
		rev_id__lte=rev.pk,
	)

	works = []
	labels: dict[str, str] = {}
	ref_models = {
		model._meta.model_name: model
		for cols in fk_columns.values()
		for model in cols.values()
	}
	if work_ids := ref_ids.pop('mediawork', set()):
		works = list(
			MediaWork.objects.filter(id__in=work_ids)
			.select_related('thumbnail_source')
			.prefetch_related('worksource_set')
		)
		# Hard-deleted works can't render as cards; fall back to a title label
		if missing := work_ids - {w.pk for w in works}:
			for pk, v in _historic_labels(MediaWork, missing, 'title').items():
				if v:
					labels[f'mediawork:{pk}'] = v
	for model_name, ids in ref_ids.items():
		model_class = ref_models[model_name]
		lf = _label_field(model_class)
		if lf is None:
			continue
		found = dict(model_class.objects.filter(pk__in=ids).values_list('pk', lf))
		if missing := ids - found.keys():
			found.update(_historic_labels(model_class, missing, lf))
		labels.update({f'{model_name}:{pk}': v for pk, v in found.items() if v})

	return {
		'works': works,
		'labels': labels,
		'deleted_rows': deleted_rows,
		'row_context': row_context,
		'changes': qq_list,
	}


def find_rev_rst(ctpk, query_pk, rev):
	"""One hop forward (original -> restored): the pk that query_pk was restored
	*to*, from a committed restored=True record or an in-flight rollback, else None.
	"""
	if q := RevisionChange.objects.filter(
		target_type_id=ctpk, target_id=query_pk, restored=True
	):
		return int(q.first().target_value)
	if (ctpk, query_pk) in rev:
		return rev[ctpk, query_pk]


def get_rev_restored(ctpk, pk):
	"""Resolve pk forward to the end of its original -> restored chain (its current
	live pk), or None if that row is deleted / not yet restored.
	"""
	cache = get_request_cache()
	rev = cache.get('rev_rst')
	rev_del = cache.get('rev_del')

	while pk is not None:
		last = pk
		pk = find_rev_rst(ctpk, pk, rev)

	# Check if deleted
	if RevisionChange.objects.filter(
		target_type_id=ctpk, target_id=last, deleted=True
	).exists() or any([ctpk == ctid and last == idd for ctid, idd, _ in rev_del]):
		return None
	else:
		return last


def add_rev_restore(ctpk, pk, new_pk):
	"""Record (in the current rollback) that pk -- resolved to the end of its
	restored chain -- has been restored as new_pk.
	"""
	assert pk != new_pk
	cache = get_request_cache()
	rev = cache.get('rev_rst')
	rev_del = cache.get('rev_del')

	while pk is not None:
		last = pk
		pk = find_rev_rst(ctpk, pk, rev)

	assert RevisionChange.objects.filter(
		target_type_id=ctpk, target_id=last, deleted=True
	).exists() or any(ctpk == ctid and last == idd for ctid, idd, _ in rev_del)
	rev[(ctpk, last)] = new_pk
	cache.set('rev_rst', rev)


def get_rev_origin(ctpk, pk, cutoff_date):
	"""Resolve pk *backward* through restored=True chains to the generation that was
	already alive at cutoff_date -- the inverse of get_rev_restored, which only walks
	forward.

	A row created by a prior rollback has no revision history before its restoration,
	so if it was born after the cutoff its pre-cutoff state must be looked up under an
	earlier generation. We stop at the first (newest) generation whose own restore
	predates the cutoff -- walking further back would read a stale generation's values.
	"""
	while True:
		prior = (
			RevisionChange.objects.filter(
				target_type_id=ctpk, target_value=str(pk), restored=True
			)
			.values_list('target_id', 'rev__date')
			.first()
		)
		if prior is None:
			return pk
		ancestor, pk_created = prior
		# `pk` was created (restored) at pk_created. If that is at/before the cutoff,
		# `pk` itself was the live row then, so its history holds the values we want.
		if pk_created <= cutoff_date:
			return pk
		pk = ancestor


def _get_all_previous_field_values(
	model_class,
	target_type_id: int,
	target_id: int,
	date: datetime,
	related_targets: dict[tuple[int, int], list[tuple[str, int, int]]],
	fields: list[str] | None = None,
) -> tuple[bool, dict[str, Any]]:
	"""
	Fetch and convert previous values for all fields of an entity before a given date.

	Args:
		model_class: The Django model class
		target_type_id: ContentType ID of the target model
		target_id: ID of the target instance
		date: Rollback to state before this date
		fields: Optional list of specific fields to fetch (fetches all if None)

	Returns:
		(True, dictionary mapping field attnames to their converted values)
		(False, missing_fields)
	"""
	query = RevisionChange.objects.filter(
		target_type_id=target_type_id,
		target_id=target_id,
		rev__date__lt=date,
		target_column__in=fields or model_class._revision_meta.tracked_fields,
	)
	qs = query.order_by('target_column', '-rev__date').distinct('target_column')
	latest_changes = dict(qs.values_list('target_column', 'target_value'))

	# Check if we found all required fields
	required_fields = fields or model_class._revision_meta.tracked_fields
	missing_fields = set(required_fields) - set(latest_changes.keys())
	if missing_fields:
		return False, missing_fields

	# Pre-fetch field objects
	related_fields = {
		field_name: model_class._meta.get_field(field_name)
		for field_name in latest_changes.keys()
	}
	model_to_ct_id = {
		field_obj.related_model: ContentType.objects.get_for_model(
			field_obj.related_model
		).id
		for field_obj in related_fields.values()
		if isinstance(field_obj, RelatedField)
	}

	result = {}
	for field_name, target_value in latest_changes.items():
		field_obj = related_fields[field_name]

		if isinstance(field_obj, RelatedField):
			if target_value is not None:
				related_ct_id = model_to_ct_id[field_obj.related_model]
				if (target_type_id, target_id) not in related_targets:
					related_targets[(target_type_id, target_id)] = [
						(field_obj.attname, related_ct_id, int(target_value))
					]
				else:
					related_targets[(target_type_id, target_id)].append(
						(
							field_obj.attname,
							related_ct_id,
							int(target_value),
						)
					)
				result[field_obj.attname] = int(target_value)  # Ostrich
			else:
				result[field_obj.attname] = None
		else:
			result[field_obj.attname] = field_obj.to_python(target_value)

	return True, result


@transaction.atomic
def rollback_entity(
	entity_id: int | str,
	entity_type: int | str,
	date: datetime,
):
	"""
	Rollback an entity to its state before a given date.

	This function restores both deleted entities and updates to existing entities
	by examining the revision history. Related entities are handled recursively.

	Args:
		entity_id: The ID of the entity to rollback
		entity_type: Either a ContentType ID (int) or model name (str)
		date: Rollback all changes that occurred on or after this date
	"""
	first_rev = Revision.objects.order_by('date').first()
	if first_rev and date <= first_rev.date:
		raise ValueError('Not allowed to rollback to before the first revision')

	def rollback_entity_rec(
		entity_id: int | str,
		entity_type: int | str,
		related_targets: dict[tuple[int, int], list[tuple[str, int, int]]],
	) -> None:
		# Normalize entity_type to ContentType ID
		if isinstance(entity_type, int):
			entity_type_id = entity_type
		elif isinstance(entity_type, str):
			entity_type_id = ContentType.objects.get(model=entity_type).id
		else:
			logger.error(f'Invalid entity_type: {entity_type}')
			return

		logger.info(f'Rolling back entity {entity_type}:{entity_id} to {date}')

		# Get all changes associated with this entity since the rollback date
		changes = RevisionChange.objects.filter(
			id__in=RevisionChangeEntity.objects.filter(
				entity_id=entity_id,
				entity_type_id=entity_type_id,
				change__rev__date__gte=date,
			).values_list('change_id', flat=True)
		)

		# Changes tagged with this entity may not tell us it's deleted if the FK/1-1 was changed to another entity before deletion
		# So we need to re-query with a correlated Table.Row
		del_rcs = (
			RevisionChange.objects.filter(rev__date__gte=date)
			.filter(
				Exists(
					changes.filter(
						target_type_id=OuterRef('target_type_id'),
						target_id=OuterRef('target_id'),
					)
				)
			)
			.filter(deleted=True)
		)

		# Recursively rollback related entities that were deleted.
		# If a related entity (FK/OneToOne pointing to this entity) was deleted,
		# we need to restore it first before we can restore this entity's references to it.
		related_entities = (
			RevisionChangeEntity.objects.filter(
				change__in=del_rcs,
				change__target_id=F('entity_id'),
				change__target_type=F('entity_type'),
			)
			.exclude(entity_id=entity_id, entity_type_id=entity_type_id)
			.values_list('entity_id', 'entity_type_id')
			.distinct()
		)
		for ent_id, ent_type_id in related_entities:
			if (
				get_rev_restored(ent_type_id, ent_id) == ent_id
				and ContentType.objects.get(id=ent_type_id)
				.model_class()
				._revision_meta.chain
				== RevisionChain.STRONG
			):
				rollback_entity_rec(ent_id, ent_type_id, related_targets)

		# Bulk fetch all unique ContentTypes we'll need
		deleted_targets = del_rcs.values_list('target_type_id', 'target_id').distinct()
		content_type_ids = set(ct_id for ct_id, _ in deleted_targets)

		# Also get content types for modified entities
		modified_targets = (
			changes.filter(deleted=False)
			.values_list('target_type_id', 'target_id')
			.distinct()
		)
		content_type_ids.update(ct_id for ct_id, _ in modified_targets)
		content_types = ContentType.objects.in_bulk(list(content_type_ids))

		# Restore deleted entities
		for target_type_id, target_id in deleted_targets:
			model_class = content_types[target_type_id].model_class()
			if model_class is None:
				logger.error(
					f'Could not get model class for ContentType ID {target_type_id}'
				)
				return

			try:
				completed, values = _get_all_previous_field_values(
					model_class, target_type_id, target_id, date, related_targets
				)
			except ValueError as e:
				logger.error(f'{e}, cannot restore deleted entity')
				raise

			if completed:
				try:
					for field_name in set(
						model_class._revision_meta.tracked_fields
					) - set(model_class._revision_meta.entity_attrs):
						FF = model_class._meta.get_field(field_name)
						if isinstance(FF, RelatedField):
							R = FF.related_model
							if not FF.null and hasattr(R, '_revision_meta'):
								assert (field_name + '_id') in values
								rel = (
									RevisionChange.objects.filter(
										target_type=ContentType.objects.get_for_model(
											R
										),
										target_id=values[field_name + '_id'],
										rev__date__lt=date,
									)
									.order_by('-rev__date')
									.first()
								)
								for ent in rel.revisionchangeentity_set.all():
									if (
										ent.entity_type_id != entity_type_id
										and not get_rev_restored(
											ent.entity_type_id, ent.entity_id
										)
									):
										rollback_entity_rec(
											ent.entity_id,
											ent.entity_type_id,
											related_targets,
										)

					# ...I'm not exactly sure why this check makes a difference, but it does
					if new_id := get_rev_restored(target_type_id, target_id):
						npk = new_id
						created = False
						model_class.objects.filter(id=new_id).update(**values)
					else:
						# N.B. we must not use select_related/prefetch_related here,
						# or update_or_create will run its internal select_for_update() over
						# the resulting outer join -- which Postgres rejects with
						# "FOR UPDATE cannot be applied to the nullable side of an outer join"
						new_instance, created = (
							model_class.objects.select_related(None)
							.prefetch_related(None)
							.update_or_create(**values)
						)
						npk = new_instance.pk
					if created:
						add_rev_restore(target_type_id, target_id, npk)
						logger.debug(
							f'Restored deleted {model_class.__name__} (old_id={target_id}, new_id={npk})'
						)
					else:
						logger.debug(
							f'Restored {model_class.__name__} (old_id={target_id}, new_id={npk}) by updating'
						)
				except Exception as e:
					logger.error(
						f'Failed to restore {model_class.__name__} (id={target_id}): {e}'
					)
					raise

		# Update modified entities using bulk operations
		# Group by (target_type_id, target_id) to batch updates per entity
		updates_by_model = {}  # model_class -> list of (instance_id, field_updates)
		delete_models = {}

		for (target_type_id, target_id), target_columns in groupby(
			changes.filter(deleted=False)
			.values_list('target_type_id', 'target_id', 'target_column')
			.order_by('target_type_id', 'target_id'),
			lambda v: (v[0], v[1]),
		):
			model_class = content_types[target_type_id].model_class()
			if model_class is None:
				logger.error(
					f'Could not get model class for ContentType ID {target_type_id}'
				)
				return

			actual_target_id = get_rev_restored(target_type_id, target_id)
			# if entry was deleted but not restored, it would have been restored earlier
			# hence only proceed if entry was restored or never deleted to begin with
			if actual_target_id:
				# however target_id may refer to a restored version of an entry deleted after this rev
				# so we need to rewind its ID if necessary
				# N.B. if the entry was restored in the current revision:
				# 	- origin_id will be the restored id
				# - _get_all_previous_field_values will not be able to fetch the changes
				# - it will enter the delete branch as desired
				origin_id = get_rev_origin(target_type_id, target_id, date)
				# Extract just the field names
				fields_to_fetch = [
					field_name_tuple[2] for field_name_tuple in target_columns
				]
				try:
					completed, values = _get_all_previous_field_values(
						model_class,
						target_type_id,
						origin_id,
						date,
						related_targets,
						fields=fields_to_fetch,
					)
				except ValueError as e:
					logger.error(f'{e}, skipping entity')
					raise
				except Exception as e:
					logger.warning(f'Could not process {model_class.__name__}: {e}')
				if completed:
					if model_class not in updates_by_model:
						updates_by_model[model_class] = []
					updates_by_model[model_class].append((actual_target_id, values))
				# Entry did not exist at this time, so delete it to complete rollback
				elif set(fields_to_fetch) == values:
					if model_class not in delete_models:
						delete_models[model_class] = []
					delete_models[model_class].append(actual_target_id)

		# Execute bulk updates per model
		for model_class, updates in updates_by_model.items():
			for instance_id, field_updates in updates:
				try:
					model_class.objects.filter(id=instance_id).update(**field_updates)
					logger.debug(
						f'Updated {model_class.__name__} (id={instance_id}) with {len(field_updates)} fields'
					)
				except Exception as e:
					logger.error(
						f'Failed to update {model_class.__name__} (id={instance_id}): {e}'
					)
					raise

		for model_class, target_ids in delete_models.items():
			model_class.objects.filter(id__in=target_ids).delete()

	related_targets = {}
	with connection.constraint_checks_disabled():
		rollback_entity_rec(entity_id, entity_type, related_targets)
		for (ctid, rid), fs in related_targets.items():
			# Apply to_active to resolve soft deletes (aliased_to/moved_to)
			changes = {}
			for f, rctid, v in fs:
				# vv is the related target's live pk if exists. Skip otherwise.
				vv = get_rev_restored(rctid, v)
				model_class = ContentType.objects.get(id=rctid).model_class()
				if (
					vv is not None
					and model_class
					and hasattr(model_class, '_revision_meta')
					and model_class._revision_meta.to_active
				):
					vv = model_class._revision_meta.to_active(
						model_class.objects.get(pk=vv)
					).pk
				changes[f] = vv
			ContentType.objects.get(id=ctid).model_class().objects.filter(
				id=get_rev_restored(ctid, rid)
			).update(**changes)


@history_router.post('rollback', auth=django_auth)
@user_is_mod  # TODO: for now
@track_revision
@with_revision_route(Route.ROLLBACK)
@transaction.atomic
def rollback(
	request: HttpRequest,
	revision_id: OtodbID,
	entity: HistoricalEntitySchema | None = None,
):
	"""
	Rollback changes of a specific revision.

	If entity is not provided: rollback all changes made IN the specified revision.
	If entity is provided: rollback that entity TO its state at the specified revision.
	"""
	add_revision_message(f'Rolled back changes in revision #{revision_id}')

	rev = get_object_or_404(Revision, id=revision_id)

	if entity is None:
		# Rollback all entities affected by this revision
		for ent in (
			RevisionChangeEntity.objects.filter(change__rev=rev)
			.values('entity_id', 'entity_type__model')
			.distinct()
			.all()
		):
			rollback_entity(ent['entity_id'], ent['entity_type__model'], rev.date)
	else:
		# Rollback specific entity TO the state at this revision
		# Get the next revision after the specified one
		next_rev = Revision.objects.filter(id__gt=revision_id).order_by('id').first()
		if next_rev is not None:
			# Rollback to the state before the next revision
			rollback_entity(entity.id, entity.entity, next_rev.date)
		# If no next revision, entity is already in that state (no-op)


@history_router.post('rollback_user', auth=django_auth)
@user_is_mod
@track_revision
@with_revision_route(Route.ROLLBACK)
@transaction.atomic
def user_rollback(request: HttpRequest, date: datetime, username: str):
	"""Rollback all changes made by a specific user since the given date."""
	add_revision_message(
		f'Rolled back changes made by {username} prior to {date.isoformat()}'
	)

	for ent in (
		RevisionChangeEntity.objects.filter(
			change__rev__date__gte=date,
			change__rev__user=get_object_or_404(Account, username=username),
		)
		.values('entity_id', 'entity_type__model')
		.distinct()
		.all()
	):
		rollback_entity(ent['entity_id'], ent['entity_type__model'], date)


@history_router.get('history', response=list[RevisionSchema])
@paginate
def history(request: HttpRequest, entity: Query[HistoricalEntitySchema]):
	query_ids = []
	match entity.entity:
		case 'mediawork':
			work = MediaWork.objects.get(id=entity.id)
			while work.moved_to:
				work = work.moved_to
			entity.id = work.pk
			cte = CTE.recursive(
				lambda cte: (
					MediaWork.objects.order_by()
					.filter(pk=work.pk)
					.values('id')
					.union(
						cte.join(
							MediaWork.objects.order_by(),
							moved_to_id=cte.col.id,
						).values('id'),
						all=True,
					)
				)
			)
			merged = (
				with_cte(cte, select=cte.join(TagWork, id=cte.col.id))
				.exclude(pk=work.pk)
				.distinct()
				.order_by()
			)
			query_ids = query_ids + [*merged.values_list('id', flat=True)]

		case 'tagwork':
			tag = TagWork.objects.get(slug=entity.id)
			if tag.aliased_to:
				tag = tag.aliased_to
			entity.id = tag.pk
			query_ids = query_ids + [*tag.aliases.values_list('id', flat=True)]
		case 'tagsong':
			tag = TagSong.objects.get(slug=entity.id)
			if tag.aliased_to:
				tag = tag.aliased_to
			entity.id = tag.pk
			query_ids = query_ids + [*tag.aliases.values_list('id', flat=True)]
		case 'mediasong':
			pass
		case 'worksource':
			pass
		case 'wikipage':
			# A wiki slug has one WikiPage row per language
			page_ids = [
				*WikiPage.objects.filter(slug=entity.id).values_list('id', flat=True)
			]
			if not page_ids:
				raise WikiPage.DoesNotExist(f'No wiki pages with slug {entity.id}')
			entity.id = page_ids[0]
			query_ids = query_ids + page_ids[1:]
	query_ids.append(entity.id)
	return (
		Revision.objects.select_related('user')
		.filter(
			id__in=Subquery(
				Revision.objects.filter(
					revisionchange__revisionchangeentity__entity_id__in=query_ids,
					revisionchange__revisionchangeentity__entity_type__model=entity.entity,
				)
				.distinct()
				.values('id')
			)
		)
		.annotate(
			index=Window(expression=RowNumber(), order_by=F('id').asc()),
			route=Subquery(
				RevisionChangeEntity.objects.filter(
					change__rev_id=OuterRef('id')
				).values('route')[:1]
			),
		)
		.order_by('-index')
	)


def _value_change_q(model: type[models.Model], column: str, value: str) -> Q:
	"""Revisions containing a change that set `model.column` to `value`"""
	return Q(
		pk__in=RevisionChange.objects.filter(
			target_type=ContentType.objects.get_for_model(model),
			target_column=column,
			target_value=value,
		).values('rev_id')
	)


def _resolve_work_tag(slug: str) -> TagWork | None:
	try:
		tag = TagWork.objects.get(slug=slugify_tag(slug))
	except TagWork.DoesNotExist:
		return None
	return tag.aliased_to or tag


def _tag_added_q(slug: str) -> Q:
	"""Revisions where tag was attached to a work"""
	tag = _resolve_work_tag(slug)
	if tag is None:
		return Q(pk__in=[])
	return _value_change_q(TagWorkInstance, 'work_tag', str(tag.pk))


def _tag_removed_q(slug: str) -> Q:
	"""Revisions where tag was detached from a work (TagWorkInstance row deleted)"""
	tag = _resolve_work_tag(slug)
	if tag is None:
		return Q(pk__in=[])
	twi_ct = ContentType.objects.get_for_model(TagWorkInstance)
	had_tag = RevisionChange.objects.filter(
		target_type=twi_ct,
		target_column='work_tag',
		target_value=str(tag.pk),
	)
	return Q(
		pk__in=RevisionChange.objects.filter(
			target_type=twi_ct,
			deleted=True,
			target_id__in=had_tag.values('target_id'),
		).values('rev_id')
	)


def _changed_field_q(
	column: str, value: str | None = None, from_value: str | None = None
) -> Q:
	"""Revisions containing a change to a tracked column with this name,
	optionally only changes that set it to `value` and/or whose previous value
	was `from_value` (raw serialized form, e.g. the integer behind an enum)."""
	flt = {'target_value': value} if value is not None else {}
	changes = RevisionChange.objects.filter(target_column=column, **flt)
	if from_value is not None:
		changes = changes.annotate(_old=_old_value_subquery).filter(_old=from_value)
	return Q(pk__in=changes.values('rev_id'))


def _is_new_q() -> Q:
	"""Revisions containing the first-ever change for an entity-level model row"""
	cts = list(
		ContentType.objects.get_for_models(
			MediaWork, TagWork, TagSong, MediaSong, WorkSource, WikiPage
		).values()
	)
	first_change = RevisionChange.objects.filter(
		rev_id=OuterRef('pk'),
		target_type__in=cts,
		deleted=False,
		restored=False,
	).filter(
		~Exists(
			RevisionChange.objects.filter(
				target_type_id=OuterRef('target_type_id'),
				target_id=OuterRef('target_id'),
				rev_id__lt=OuterRef('rev_id'),
			)
		)
	)
	return Q(Exists(first_change))


def _change_flag_q(**flags) -> Q:
	return Q(Exists(RevisionChange.objects.filter(rev_id=OuterRef('pk'), **flags)))


@history_router.get('search', response=list[RevisionSchema])
@paginate
def search(
	request: HttpRequest,
	username: str | None = None,
	routes: list[Route] | None = Query(None),
	entity: HistoricalEntities | None = None,
	reason: str | None = None,
	since: date | None = None,
	until: date | None = None,
	is_new: bool | None = None,
	is_deleted: bool | None = None,
	added_tags: list[str] | None = Query(None),
	removed_tags: list[str] | None = Query(None),
	changed_tags: list[str] | None = Query(None),
	changed_field: str | None = None,
	changed_value: str | None = None,
	changed_from: str | None = None,
):
	q = Q()
	if username:
		q &= Q(user__username__iexact=username)
	if routes:
		q &= Q(
			Exists(
				RevisionChangeEntity.objects.filter(
					change__rev_id=OuterRef('pk'), route__in=routes
				)
			)
		)
	if entity is not None:
		q &= Q(
			Exists(
				RevisionChangeEntity.objects.filter(
					change__rev_id=OuterRef('pk'),
					entity_type__model=entity.value,
				)
			)
		)
	if reason:
		q &= Q(message__icontains=reason)
	if since is not None:
		q &= Q(date__date__gte=since)
	if until is not None:
		q &= Q(date__date__lte=until)
	if is_new is not None:
		q &= _is_new_q() if is_new else ~_is_new_q()
	if is_deleted is not None:
		flag = _change_flag_q(deleted=True)
		q &= flag if is_deleted else ~flag
	for slug in added_tags or []:
		q &= _tag_added_q(slug)
	for slug in removed_tags or []:
		q &= _tag_removed_q(slug)
	for slug in changed_tags or []:
		q &= _tag_added_q(slug) | _tag_removed_q(slug)
	if changed_field:
		q &= _changed_field_q(changed_field, changed_value, changed_from)

	return (
		Revision.objects.select_related('user')
		.filter(q)
		.annotate(
			route=Subquery(
				RevisionChangeEntity.objects.filter(
					change__rev_id=OuterRef('id')
				).values('route')[:1]
			)
		)
		.order_by('-id')
	)
