"""Application-side runtime for the DB-trigger revision system.

Capture lives in Postgres (see ``otodb/revision_codegen.py`` /
``otodb/sql/revision_triggers.sql``). This module is the thin app surface that remains
after the ORM capture was stripped:

* ``db_revision(...)`` -- open a transaction, stamp it so the triggers attribute + group
  the writes into one Revision, then fan out its side effects on exit.
* ``fan_out(revision_id)`` -- the subscription/notification side effects, driven
  entirely by the persisted revision rows, so it is call-from-anywhere (Django,
  Litestar, a future axum).

Revision merging is intentionally deferred (design in REVISION_TRIGGERS_EVAL.md §11/§13).
"""

from contextlib import contextmanager

from django.db import connection, transaction


def _stamp(user_id, message, route):
	with connection.cursor() as cursor:
		cursor.execute(
			"SELECT set_config('otodb.user_id', %s, true),"
			" set_config('otodb.message', %s, true),"
			" set_config('otodb.route', %s, true),"
			" set_config('otodb.rev_id', '', true)",
			[
				'' if user_id is None else str(user_id),
				message or '',
				str(int(route)),
			],
		)


def _current_revision_id():
	with connection.cursor() as cursor:
		cursor.execute(
			"SELECT nullif(current_setting('otodb.rev_id', true), '')::bigint"
		)
		return cursor.fetchone()[0]


@contextmanager
def db_revision(user=None, message='', route=0):
	"""Open a transaction, stamp it for the capture triggers, and on clean exit fan out
	the resulting Revision's side effects.

	``user`` may be a user instance, an id, or None (anonymous). Resetting
	``otodb.rev_id`` on entry starts a fresh Revision for this block.
	"""
	user_id = getattr(user, 'pk', user)
	with transaction.atomic():
		_stamp(user_id, message, route)
		yield
		revision_id = _current_revision_id()
		if revision_id is not None:
			fan_out(revision_id)


def fan_out(revision_id):
	"""Notify subscribers of the changed rows, auto-subscribe the (active) actor to the
	routed entities, then drop subscriptions whose row was deleted -- all from persisted
	rows, in the current transaction.

	Subscriptions persist across changes (a subscriber is notified of every revision
	touching the row); one is deleted only when the subscribed row itself is, since the
	generic FK cannot cascade. Pruning runs LAST so a subscription to a row deleted in
	this revision -- pre-existing or just auto-created -- never outlives it.
	``IS DISTINCT FROM`` excludes the actor while still notifying everyone on an
	anonymous (NULL-user) edit, matching Python ``sub != request.user.id``.
	"""
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			WITH touched AS (
				SELECT DISTINCT target_type_id AS et, target_id AS eid
				FROM otodb_revisionchange WHERE rev_id = %(rev)s
			)
			INSERT INTO otodb_notification (target_id, revision_id, reason, dismissed, created_at)
			SELECT DISTINCT s.subscriber_id, %(rev)s, 0, false, now()
			FROM otodb_subscription s
			JOIN touched t ON s.entity_type_id = t.et AND s.entity_id = t.eid
			JOIN otodb_revision r ON r.id = %(rev)s
			WHERE s.subscriber_id IS DISTINCT FROM r.user_id
			""",
			{'rev': revision_id},
		)
		cursor.execute(
			"""
			INSERT INTO otodb_subscription (subscriber_id, entity_type_id, entity_id)
			SELECT r.user_id, rce.entity_type_id, rce.entity_id
			FROM otodb_revision r
			JOIN otodb_revisionchange rc ON rc.rev_id = r.id
			JOIN otodb_revisionchangeentity rce ON rce.change_id = rc.id
			JOIN account_account a ON a.id = r.user_id AND a.is_active
			WHERE r.id = %(rev)s
			ON CONFLICT (subscriber_id, entity_type_id, entity_id) DO NOTHING
			""",
			{'rev': revision_id},
		)
		cursor.execute(
			"""
			DELETE FROM otodb_subscription s
			USING otodb_revisionchange rc
			WHERE rc.rev_id = %(rev)s AND rc.deleted
				AND s.entity_type_id = rc.target_type_id
				AND s.entity_id = rc.target_id
			""",
			{'rev': revision_id},
		)
