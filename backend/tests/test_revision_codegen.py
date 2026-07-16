"""The committed trigger SQL must match fresh codegen output.

Migration 0121 installs ``generate_sql()`` live, so a stale ``revision_triggers.sql``
means the committed artifact no longer documents what a fresh migrate installs -- and a
spec change was made without regenerating. Django-free on purpose: this check (also
available as ``python -m otodb.revision_codegen --check``) survives the migration off
Django, unlike ``test_revision_spec_parity``.
"""

from pathlib import Path

from otodb import revision_codegen


def test_committed_sql_matches_codegen():
	artifact = Path(revision_codegen.__file__).parent / 'sql' / 'revision_triggers.sql'
	assert artifact.read_text(encoding='utf-8') == revision_codegen.generate_sql(), (
		'otodb/sql/revision_triggers.sql is stale -- regenerate:'
		' python -m otodb.revision_codegen > otodb/sql/revision_triggers.sql'
	)
