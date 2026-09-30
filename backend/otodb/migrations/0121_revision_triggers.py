"""Does nothing now. The revision triggers used to be installed here.

They are now installed after every `migrate` instead (see `otodb/apps.py`), so they
always match the current spec. This file stays so old databases keep the same
migration history.

No FK changes are needed: Django's Python-side cascade (on_delete=CASCADE) issues real
DELETE SQL on child tables, which fires the child capture triggers per row.
"""

from django.db import migrations


class Migration(migrations.Migration):
	dependencies = [
		('otodb', '0120_worksource_pending_since'),
	]

	operations = []
