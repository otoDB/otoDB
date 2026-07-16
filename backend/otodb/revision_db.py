"""Application-side runtime for the DB-trigger revision system.

Capture lives in Postgres (see ``otodb/revision_codegen.py`` /
``otodb/sql/revision_triggers.sql``). This module is the thin app surface that remains
after the ORM capture was stripped:

* ``db_revision(...)`` -- open a transaction, stamp it so the triggers attribute + group
  the writes into one Revision, then fan out its side effects on exit.
* ``fan_out(revision_id)`` -- invokes the codegen'd ``otodb_fan_out`` DB function
  holding the subscription/notification side effects; driven entirely by the persisted
  revision rows, so any backend triggers identical side effects with one call.

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
	"""Run the Revision's side effects: notify subscribers of the changed rows,
	auto-subscribe the (active) actor to the routed entities, prune subscriptions of
	deleted rows. The logic lives in the codegen'd ``otodb_fan_out`` DB function (see
	``revision_codegen._BASE_SQL`` for the semantics), so every backend -- Django,
	Litestar, a future axum -- triggers identical side effects with this one call in
	its write transaction."""
	with connection.cursor() as cursor:
		cursor.execute('SELECT otodb_fan_out(%s)', [revision_id])
