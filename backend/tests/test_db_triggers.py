"""The committed trigger SQL must match fresh codegen output.

`install_db_triggers()` runs `generate_sql()` live after every migrate, so a stale
`db_triggers.sql` means the committed artifact no longer documents what a fresh migrate
installs -- and a spec change was made without regenerating. Django-free on purpose:
this check (also available as `python -m otodb.db_triggers --check`) survives the
migration off Django, unlike `test_revision_spec_parity`.
"""

from pathlib import Path

from otodb import db_triggers


def test_committed_sql_matches_codegen():
	artifact = Path(db_triggers.__file__).parent / 'sql' / 'db_triggers.sql'
	assert artifact.read_text(encoding='utf-8') == db_triggers.generate_sql(), (
		'otodb/sql/db_triggers.sql is stale -- regenerate:'
		' python -m otodb.db_triggers > otodb/sql/db_triggers.sql'
	)
