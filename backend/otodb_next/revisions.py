"""Revision tracking for SQLAlchemy models -- a port of the WRITE path of
otodb/models/revision.py + otodb/api/common.py `_commit_pending_revision`.

Same tables, same row shapes, same semantics; the read side
(otodb/api/history.py) stays on Django until those endpoints migrate.
Parity is asserted row-for-row in tests/otodb_next/test_revisions.py.

Design notes (each verified empirically, July 2026 -- see MIGRATION_BRIEF §5):

- Changes are captured in mapper-level after_insert/after_update/after_delete
  events, NOT before_flush: FK column history is not yet populated in
  before_flush when only the relationship attribute was assigned, and
  cascade-deleted children fire their own per-child after_delete.
- The per-request accumulator (`RevisionCollector`) lives in ``session.info``,
  where mapper events can reach it via ``object_session(target)``. Enter a
  scope with :func:`revision_scope`; mutations outside a scope are logged as
  WITHOUT REVISION TRACKING (matching the Django behavior) and lost.
- Serialization parity with Django's ``value_to_string`` for every tracked
  field type in this app is exactly ``None -> NULL else str(value)``.
- Creations record ALL tracked fields including NULLs (Django's dirtyfields
  marks every field dirty while ``_state.adding``).
- Bulk ``session.execute(update()/delete())`` against tracked models raises
  :class:`RevisionBypassError` unless run with
  ``execution_options={'revision_exempt': True}``. This guard is session-level
  only; raw ``text()`` and connection-level SQL are not policed (deliberate
  perf call -- convention and review own that path).
- Programmatic revisions (scheduler jobs, imports) attribute to the system bot
  via :func:`system_user` -- the port of ``Account.get_system()``.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import sqlalchemy as sa
from litestar import Litestar
from sqlalchemy import event, orm
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from otodb_next.models import (
	Account,
	Base,
	ContentType,
	Notification,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
	Subscription,
)

logger = logging.getLogger(__name__)

_INFO_KEY = 'otodb_revision_collector'
_registry: dict[type, _Tracked] = {}
_guard_installed = False
_system_user: tuple[int, bool] | None = None


class RevisionBypassError(Exception):
	"""A bulk UPDATE/DELETE would silently skip revision tracking."""


@dataclass
class _Tracked:
	"""Runtime revision config for one model, derived by init_tracking() from
	the model's ``__revision__`` dict (which has exactly Django's RevisionMeta
	shape: ``tracked_fields`` + ``entity_attrs``) and its SQLAlchemy mapper.
	"""

	model: type
	ct_key: tuple[str, str]  # (app_label, model) in django_content_type
	tracked: dict[str, str]  # Django field name -> instrumented attribute name
	# entity attr ('self' or a *_id attribute name) -> entity's ct key
	# ('self' entities use this model's own content type)
	entities: list[tuple[str, tuple[str, str] | None]]
	ct_id: int | None = None
	entity_ct_ids: list[int] = field(default_factory=list)


class RevisionCollector:
	"""Per-scope accumulator; the port of the request-cache rev/rev_del/rev_rst
	keys. Lives in session.info while a revision_scope is active.
	"""

	def __init__(
		self, *, user_id: int | None, user_is_active: bool, message: str, route: int
	):
		self.user_id = user_id
		self.user_is_active = user_is_active
		self.message = message
		self.route = route
		# (ct_id, pk, django_field) -> (ents, serialized value)
		self.rev: dict[tuple[int, int, str], tuple[tuple, str | None]] = {}
		# (ct_id, pk, ents)
		self.rev_del: list[tuple[int, int, tuple]] = []
		# (ct_id, pk) -> restored-as pk
		self.rev_rst: dict[tuple[int, int], int] = {}

	def add_message(self, message: str) -> None:
		"""Port of otodb.revisions.add_revision_message."""
		self.message = self.message + ('\n' if self.message else '') + message

	def __bool__(self) -> bool:
		return bool(self.rev or self.rev_del or self.rev_rst)


def _serialize(value) -> str | None:
	"""Django value_to_string parity for every tracked field type in this app."""
	return None if value is None else str(value)


def _ents(cfg: _Tracked, target) -> tuple:
	return tuple(
		target.id if attr == 'self' else getattr(target, attr)
		for attr, _ in cfg.entities
	)


def _collector(cfg: _Tracked, target) -> RevisionCollector | None:
	session = orm.object_session(target)
	col = session.info.get(_INFO_KEY) if session is not None else None
	if col is None:
		logger.warning(
			'MUTATING %s (pk=%s) WITHOUT REVISION TRACKING',
			type(target).__name__,
			target.id,
		)
	return col


def _after_insert(cfg: _Tracked, mapper, connection, target) -> None:
	if (col := _collector(cfg, target)) is None:
		return
	# Creation records ALL tracked fields, incl. NULLs (dirtyfields parity)
	ents = _ents(cfg, target)
	for django_name, attr in cfg.tracked.items():
		col.rev[(cfg.ct_id, target.id, django_name)] = (
			ents,
			_serialize(getattr(target, attr)),
		)


def _after_update(cfg: _Tracked, mapper, connection, target) -> None:
	if (col := _collector(cfg, target)) is None:
		return
	insp = sa.inspect(target)
	ents = _ents(cfg, target)
	for django_name, attr in cfg.tracked.items():
		if insp.attrs[attr].history.has_changes():
			col.rev[(cfg.ct_id, target.id, django_name)] = (
				ents,
				_serialize(getattr(target, attr)),
			)


def _after_delete(cfg: _Tracked, mapper, connection, target) -> None:
	if (col := _collector(cfg, target)) is None:
		return
	col.rev_del.append((cfg.ct_id, target.id, _ents(cfg, target)))


def _guard(ctx: orm.ORMExecuteState) -> None:
	if not (ctx.is_update or ctx.is_delete):
		return
	if ctx.execution_options.get('revision_exempt'):
		return
	mapper = ctx.bind_mapper
	if mapper is not None and mapper.class_ in _registry:
		raise RevisionBypassError(
			f'bulk {"UPDATE" if ctx.is_update else "DELETE"} on revision-tracked '
			f'{mapper.class_.__name__} bypasses tracking -- mutate instances via '
			f"the ORM, or pass execution_options={{'revision_exempt': True}} if "
			f'revisions are handled manually'
		)


def init_tracking(base: type) -> None:
	"""Register event listeners for every model in `base`'s registry that
	declares a ``__revision__`` dict (the port of Django's RevisionMeta).

	Runs at the bottom of this module -- importing it activates tracking, the
	way RevisionTrackedModel.__init_subclass__ does on the Django side.
	Idempotent, so re-invoking (e.g. after defining late models) is safe.
	"""
	global _guard_installed
	if not _guard_installed:
		event.listen(orm.Session, 'do_orm_execute', _guard)
		_guard_installed = True

	def ct_key(table_name: str) -> tuple[str, str]:
		# Django's default table naming is f'{app_label}_{model_name}', which
		# is also exactly how django_content_type rows are keyed.
		app_label, _, model_name = table_name.partition('_')
		return app_label, model_name

	def column_attr(mapper, field_name: str) -> str:
		# Django field names address FKs without the _id suffix; the mapper
		# knows which is which.
		fk = f'{field_name}_id'
		return fk if fk in mapper.columns else field_name

	def entity(mapper, attr: str) -> tuple[str, tuple[str, str] | None]:
		if attr == 'self':
			return 'self', None
		col = column_attr(mapper, attr)
		fk = next(iter(mapper.columns[col].foreign_keys))
		return col, ct_key(fk.column.table.name)

	for mapper in base.registry.mappers:
		cls = mapper.class_
		spec = cls.__dict__.get('__revision__')
		if spec is None or cls in _registry:
			continue
		cfg = _Tracked(
			model=cls,
			ct_key=ct_key(mapper.local_table.name),
			tracked={f: column_attr(mapper, f) for f in spec['tracked_fields']},
			entities=[entity(mapper, a) for a in spec['entity_attrs']],
		)
		_registry[cls] = cfg
		event.listen(
			cls, 'after_insert', lambda m, c, t, cfg=cfg: _after_insert(cfg, m, c, t)
		)
		event.listen(
			cls, 'after_update', lambda m, c, t, cfg=cfg: _after_update(cfg, m, c, t)
		)
		event.listen(
			cls, 'after_delete', lambda m, c, t, cfg=cfg: _after_delete(cfg, m, c, t)
		)


async def load_content_types(source) -> None:
	"""Resolve every registered config's content-type ids -- the only startup
	work revision tracking needs (post-Django these could become constants).

	`source` is either the Litestar app (usable directly as
	``on_startup=[revisions.load_content_types]``) or any async executor
	(AsyncConnection/AsyncSession) for tests and scripts.
	"""
	stmt = sa.select(ContentType.app_label, ContentType.model, ContentType.id)
	if isinstance(source, Litestar):
		# SQLAlchemyAsyncConfig.engine_app_state_key default
		engine = source.state['db_engine']
		async with engine.connect() as conn:
			rows = await conn.execute(stmt)
	else:
		rows = await source.execute(stmt)
	ct_map = {(app, model): id_ for app, model, id_ in rows}
	for cfg in _registry.values():
		cfg.ct_id = ct_map[cfg.ct_key]
		cfg.entity_ct_ids = [
			cfg.ct_id if ct is None else ct_map[tuple(ct)] for _, ct in cfg.entities
		]


async def system_user(session: AsyncSession) -> tuple[int, bool]:
	"""Port of ``Account.get_system()`` for programmatic revisions (scheduler
	jobs, imports): returns ``(user_id, is_active)`` for the system bot, ready
	to pass to :func:`revision_scope`. The bot is created with is_active=False
	by migration account.0008, which is what excludes it from auto-subscribe.
	Cached after the first lookup (the row is stable).
	"""
	global _system_user
	if _system_user is None:
		# config single source while Django exists (see MIGRATION_BRIEF)
		from django.conf import settings

		_system_user = (
			(
				await session.execute(
					sa.select(Account.id, Account.is_active).where(
						Account.username == settings.OTODB_SYSTEM_BOT_USERNAME
					)
				)
			)
			.one()
			._tuple()
		)
	return _system_user


async def _find_rev_rst(session: AsyncSession, col, ct_id: int, pk: int):
	"""Port of history.find_rev_rst: one hop forward through restore records."""
	val = await session.scalar(
		sa.select(RevisionChange.target_value)
		.where(
			RevisionChange.target_type_id == ct_id,
			RevisionChange.target_id == pk,
			RevisionChange.restored.is_(True),
		)
		.limit(1)
	)
	if val is not None:
		return int(val)
	return col.rev_rst.get((ct_id, pk))


async def _get_rev_restored(session: AsyncSession, col, ct_id: int, pk: int):
	"""Port of history.get_rev_restored: resolve pk to the end of its
	original -> restored chain, or None if that row is deleted.
	"""
	last = pk
	while pk is not None:
		last = pk
		pk = await _find_rev_rst(session, col, ct_id, pk)

	deleted_in_db = await session.scalar(
		sa.select(
			sa.exists().where(
				RevisionChange.target_type_id == ct_id,
				RevisionChange.target_id == last,
				RevisionChange.deleted.is_(True),
			)
		)
	)
	if deleted_in_db or any(
		ct_id == ctid and last == idd for ctid, idd, _ in col.rev_del
	):
		return None
	return last


async def commit_pending(session: AsyncSession, col: RevisionCollector) -> int | None:
	"""Port of _commit_pending_revision: materialize the collector into one
	Revision + its change/entity/subscription/notification rows. Runs inside
	the caller's transaction; returns the new revision id (None if no-op).
	"""
	if not col:
		return None

	revision = Revision(user_id=col.user_id, message=col.message)
	session.add(revision)
	await session.flush()

	changes: list[RevisionChange] = []
	# (change, entity_ct_ids, ents) triples awaiting entity-row creation
	pending_entities: list[tuple[RevisionChange, list[int], tuple]] = []

	cfg_by_ct = {cfg.ct_id: cfg for cfg in _registry.values()}

	# Deletions first, deduped -- mirrors _commit_pending_revision
	seen_deletions = {}
	for ct_id, pk, ents in col.rev_del:
		if (ct_id, pk) in seen_deletions:
			continue
		seen_deletions[(ct_id, pk)] = ents
		change = RevisionChange(
			rev_id=revision.id, target_type_id=ct_id, target_id=pk, deleted=True
		)
		changes.append(change)
		pending_entities.append((change, cfg_by_ct[ct_id].entity_ct_ids, ents))

	for (ct_id, pk, django_name), (ents, value) in col.rev.items():
		change = RevisionChange(
			rev_id=revision.id,
			target_type_id=ct_id,
			target_id=pk,
			target_column=django_name,
			target_value=value,
		)
		changes.append(change)
		pending_entities.append((change, cfg_by_ct[ct_id].entity_ct_ids, ents))

	for (ct_id, pk), to_pk in col.rev_rst.items():
		changes.append(
			RevisionChange(
				rev_id=revision.id,
				target_type_id=ct_id,
				target_id=pk,
				target_value=str(to_pk),
				restored=True,
			)
		)

	# Notify-and-unsubscribe: subscriptions sitting on the CHANGED ROWS
	# (not the routed entities) -- faithful to the Django commit path.
	target_keys = list(
		dict.fromkeys(
			[(ct, pk) for (ct, pk) in seen_deletions]
			+ [(ct, pk) for ct, pk, _ in col.rev]
		)
	)
	subscribers: set[int] = set()
	if target_keys:
		key_tuple = sa.tuple_(Subscription.entity_type_id, Subscription.entity_id)
		subscribers = {
			row.subscriber_id
			for row in await session.execute(
				sa.select(Subscription.subscriber_id).where(key_tuple.in_(target_keys))
			)
		}
		if subscribers:
			await session.execute(
				sa.delete(Subscription).where(key_tuple.in_(target_keys))
			)

	session.add_all(changes)
	await session.flush()

	# Entity routing + auto-subscribe (active users only, excl. system bot)
	entity_rows: list[RevisionChangeEntity] = []
	subscriptions: list[dict] = []
	for change, entity_ct_ids, ents in pending_entities:
		for entity_ct_id, ent_pk in zip(entity_ct_ids, ents):
			if not ent_pk:
				continue
			ent_pk = (
				await _get_rev_restored(session, col, entity_ct_id, ent_pk) or ent_pk
			)
			entity_rows.append(
				RevisionChangeEntity(
					change_id=change.id,
					entity_type_id=entity_ct_id,
					entity_id=ent_pk,
					route=col.route,
				)
			)
			if col.user_is_active and col.user_id is not None:
				subscriptions.append(
					{
						'subscriber_id': col.user_id,
						'entity_type_id': entity_ct_id,
						'entity_id': ent_pk,
					}
				)

	if entity_rows:
		session.add_all(entity_rows)
	if subscriptions:
		# bulk_create(ignore_conflicts=True) parity
		subscriptions = list({tuple(s.items()): s for s in subscriptions}.values())
		await session.execute(
			pg_insert(Subscription).values(subscriptions).on_conflict_do_nothing()
		)
	session.add_all(
		Notification(revision_id=revision.id, target_id=sub)
		for sub in subscribers
		if sub != col.user_id
	)
	await session.flush()
	return revision.id


@asynccontextmanager
async def revision_scope(
	session: AsyncSession,
	*,
	user_id: int | None,
	user_is_active: bool = True,
	message: str = '',
	route: int = 0,  # Route.UNKNOWN
):
	"""Group all tracked mutations on `session` into one Revision -- the port of
	both `track_revision` (wrap a request handler's session) and the
	`revision()` context manager (programmatic/scheduler use).

	Commits the pending revision into the caller's transaction on clean exit;
	the caller still owns COMMIT/ROLLBACK.
	"""
	col = RevisionCollector(
		user_id=user_id, user_is_active=user_is_active, message=message, route=route
	)
	info = (
		session.sync_session.info if isinstance(session, AsyncSession) else session.info
	)
	if _INFO_KEY in info:
		raise RuntimeError('revision_scope is already active on this session')
	info[_INFO_KEY] = col
	try:
		yield col
		await session.flush()  # fire mapper events for any un-flushed mutations
		await commit_pending(session, col)
	finally:
		info.pop(_INFO_KEY, None)


# Importing this module activates tracking for every __revision__-declaring
# model, the way RevisionTrackedModel.__init_subclass__ does on the Django side.
init_tracking(Base)
