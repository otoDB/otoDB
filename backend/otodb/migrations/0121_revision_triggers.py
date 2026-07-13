"""Install the DB revision-capture triggers for every tracked model.

The SQL is generated Django-free from otodb/revision_spec.py (see
otodb/revision_codegen.py). All statements are CREATE OR REPLACE, so re-applying is
idempotent; when the spec changes, regenerate and add a follow-up migration.

No FK changes are needed: Django's Python-side cascade (on_delete=CASCADE) issues real
DELETE SQL on child tables, which fires the child capture triggers per row.
"""

from django.db import migrations

from otodb.revision_codegen import generate_drop_sql, generate_sql


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0120_worksource_pending_since'),
	]

	operations = [
		migrations.RunSQL(sql=generate_sql(), reverse_sql=generate_drop_sql()),
	]
