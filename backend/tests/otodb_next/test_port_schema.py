"""Guard the otodb_next models against schema drift: Django migrations own the
DDL (see otodb_next/models/base.py), so every declared column/type/PK/FK must
keep matching the real, migrations-created schema. Runs against the pytest
test database via reflection.

Deliberate deltas are allow-listed; everything else is a failure telling you a
migration and the mirror models diverged.
"""

import pytest
import sqlalchemy as sa

from otodb_next.models import Base
from tests.otodb_next.conftest import sa_url

# DB foreign keys deliberately NOT declared on the models (unported models;
# the DB still enforces them) -- keep in sync with the TODO(port) markers.
ALLOWED_FK_OMISSIONS = {
	('otodb_notification', 'comment_id'),
	('otodb_notification', 'threadpost_id'),
}


@pytest.mark.django_db
def test_models_match_live_schema(db):
	engine = sa.create_engine(sa_url())
	try:
		reflected = sa.MetaData()
		reflected.reflect(engine, only=list(Base.metadata.tables))
		dialect = engine.dialect

		problems = []
		for tname, ours in sorted(Base.metadata.tables.items()):
			theirs = reflected.tables[tname]
			ours_cols = {c.name for c in ours.columns}
			theirs_cols = {c.name for c in theirs.columns}
			for missing in sorted(theirs_cols - ours_cols):
				problems.append(f'{tname}: column {missing!r} in DB, not in model')
			for extra in sorted(ours_cols - theirs_cols):
				problems.append(f'{tname}: column {extra!r} in model, not in DB')

			for cname in sorted(ours_cols & theirs_cols):
				oc, tc = ours.c[cname], theirs.c[cname]
				if oc.type.compile(dialect) != tc.type.compile(dialect):
					problems.append(
						f'{tname}.{cname}: type model={oc.type.compile(dialect)} '
						f'db={tc.type.compile(dialect)}'
					)
				if oc.nullable != tc.nullable:
					problems.append(
						f'{tname}.{cname}: nullable model={oc.nullable} '
						f'db={tc.nullable}'
					)
				if oc.primary_key != tc.primary_key:
					problems.append(f'{tname}.{cname}: primary_key mismatch')

				ofk = {
					f'{f.column.table.name}.{f.column.name}' for f in oc.foreign_keys
				}
				tfk = {
					f'{f.column.table.name}.{f.column.name}' for f in tc.foreign_keys
				}
				if ofk - tfk:
					problems.append(f'{tname}.{cname}: FK {ofk - tfk} not in DB')
				if (tfk - ofk) and (tname, cname) not in ALLOWED_FK_OMISSIONS:
					problems.append(
						f'{tname}.{cname}: DB FK {tfk - ofk} not declared '
						f'(allow-list it only with a TODO(port) marker)'
					)

			# every unique constraint the model declares must exist in the DB
			def uniques(t):
				out = set()
				for c in t.constraints:
					if isinstance(c, sa.UniqueConstraint):
						out.add(tuple(sorted(col.name for col in c.columns)))
				for i in t.indexes:
					if i.unique:
						out.add(tuple(sorted(col.name for col in i.columns)))
				return out

			for extra in sorted(uniques(ours) - uniques(theirs)):
				problems.append(f'{tname}: unique {extra} in model, not in DB')

		assert not problems, 'model/schema drift:\n' + '\n'.join(
			f'  {p}' for p in problems
		)
	finally:
		engine.dispose()
