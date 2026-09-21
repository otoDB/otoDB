"""
Application-side runtime for the DB-backed revision system.
"""

from contextlib import contextmanager

from django.db import connection, transaction

_SETTINGS = ('otodb.user_id', 'otodb.message', 'otodb.route', 'otodb.rev_id')
_READ_STAMP = 'SELECT ' + ', '.join(f"current_setting('{s}', true)" for s in _SETTINGS)
_WRITE_STAMP = 'SELECT ' + ', '.join(f"set_config('{s}', %s, true)" for s in _SETTINGS)


@contextmanager
def db_revision(user=None, message='', route=0):
	"""
	Open a transaction and stamp it for the capture triggers.

	`user` may be a user instance, an id, or None -- which stamps no author, so the
	trigger attributes the Revision to the system bot (account id 1). Resetting
	`otodb.rev_id` on entry starts a fresh Revision for this block.
	"""
	user_id = getattr(user, 'pk', user)
	stamp = [
		'' if user_id is None else str(user_id),
		message or '',
		str(int(route)),
		'',
	]
	nested = connection.in_atomic_block
	with transaction.atomic():
		with connection.cursor() as cursor:
			if nested:
				cursor.execute(_READ_STAMP)
				enclosing = [value or '' for value in cursor.fetchone()]
			cursor.execute(_WRITE_STAMP, stamp)
		yield
		if nested:
			with connection.cursor() as cursor:
				cursor.execute(_WRITE_STAMP, enclosing)
