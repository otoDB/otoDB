"""Behavior tests for otodb_next.revisions itself -- the permanent revision
writer. Django-parity comparisons (migration scaffolding) live in
test_port_revisions.py instead.
"""

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker

from otodb_next import revisions
from otodb_next.models import TagWorkConnection
from tests.otodb_next.conftest import run_async


def test_bulk_write_guard(port_engine):
	"""Bulk UPDATE/DELETE against tracked models raises RevisionBypassError;
	revision_exempt opts out for writes that handle revisions manually."""

	async def scenario():
		async with async_sessionmaker(port_engine)() as s:
			with pytest.raises(revisions.RevisionBypassError):
				await s.execute(sa.update(TagWorkConnection).values(site=9))
			with pytest.raises(revisions.RevisionBypassError):
				await s.execute(sa.delete(TagWorkConnection))
			await s.execute(
				sa.update(TagWorkConnection).values(site=9),
				execution_options={'revision_exempt': True},
			)
			await s.rollback()

	run_async(scenario())


def test_revision_scope_is_exclusive(port_engine):
	"""One revision scope per session -- nesting is a programming error."""

	async def scenario():
		async with async_sessionmaker(port_engine)() as s:
			async with revisions.revision_scope(s, user_id=None):
				with pytest.raises(RuntimeError):
					async with revisions.revision_scope(s, user_id=None):
						pass  # pragma: no cover

	run_async(scenario())
