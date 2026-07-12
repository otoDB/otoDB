"""Shared fixtures for otodb_next tests.

Port tests talk to the pytest test database over the app's own SQLAlchemy
engine. Where rows must be visible across connections (endpoint tests: the
auth middleware and handlers read on the app's own sessions), fixtures COMMIT
and clean up after themselves -- Django's per-test transaction can't cover
another connection.
"""

import asyncio
import selectors
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture(autouse=True)
def enable_request_cache():
	"""Override the DB-backed autouse fixture from the parent conftest -- these
	tests must not require a database unless they ask for one."""
	yield


def run_async(coro):
	# psycopg-async can't run on Windows' default ProactorEventLoop
	return asyncio.run(
		coro,
		loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
	)


def sa_url():
	"""SQLAlchemy URL for the (already created) pytest test database."""
	from django.db import connection

	sd = connection.settings_dict
	return sa.engine.URL.create(
		'postgresql+psycopg',
		username=sd['USER'],
		password=sd['PASSWORD'] or None,
		host=sd['HOST'] or 'localhost',
		port=int(sd['PORT']) if sd['PORT'] else None,
		database=sd['NAME'],
	)


@pytest.fixture
def port_engine(db):
	# lock_timeout: unique-key overlap with Django's open test transaction
	# must fail fast, not hang (see test_port_revisions docstring)
	engine = create_async_engine(
		sa_url(), connect_args={'options': '-c lock_timeout=5000'}
	)
	yield engine
	run_async(engine.dispose())


PORT_USER_LEVELS = {'restricted': 10, 'member': 20, 'editor': 40}


@pytest.fixture
def port_users(port_engine):
	"""COMMITTED accounts + signed django_session rows per role (session key:
	``port<role>``, cookie via login()). Teardown sweeps every revision-side
	effect attributed to these users (revisions, changes, entities,
	subscriptions, notifications), so endpoint tests only clean their own
	domain rows.
	"""
	from otodb_next.models import (
		Account,
		Notification,
		Revision,
		RevisionChange,
		RevisionChangeEntity,
		Subscription,
	)
	from tests.otodb_next.test_session_middleware import (
		PASSWORD_HASH,
		auth_hash,
		encode_session,
	)

	Session = async_sessionmaker(port_engine, expire_on_commit=False)
	now = datetime.now(timezone.utc)

	async def setup():
		ids = {}
		async with Session() as s:
			for role, level in PORT_USER_LEVELS.items():
				acct = Account(
					username=f'port_{role}',
					email=f'port_{role}@test.invalid',
					password=PASSWORD_HASH,
					level=level,
					email_activated=True,
					is_active=True,
					date_created=now,
				)
				s.add(acct)
				await s.flush()
				ids[role] = acct.id
				await s.execute(
					sa.text(
						'INSERT INTO django_session'
						' (session_key, session_data, expire_date)'
						' VALUES (:key, :data, :expires)'
					),
					{
						'key': f'port{role}',
						'data': encode_session(
							{
								'_auth_user_id': str(acct.id),
								'_auth_user_hash': auth_hash(),
							}
						),
						'expires': now + timedelta(days=1),
					},
				)
			await s.commit()
		return ids

	async def teardown(ids):
		uids = list(ids.values())
		async with Session() as s:
			rev_ids = sa.select(Revision.id).where(Revision.user_id.in_(uids))
			change_ids = sa.select(RevisionChange.id).where(
				RevisionChange.rev_id.in_(rev_ids)
			)
			await s.execute(
				sa.delete(Notification).where(Notification.revision_id.in_(rev_ids))
			)
			await s.execute(
				sa.delete(RevisionChangeEntity).where(
					RevisionChangeEntity.change_id.in_(change_ids)
				)
			)
			await s.execute(
				sa.delete(RevisionChange).where(RevisionChange.rev_id.in_(rev_ids))
			)
			await s.execute(sa.delete(Revision).where(Revision.id.in_(rev_ids)))
			await s.execute(
				sa.delete(Subscription).where(Subscription.subscriber_id.in_(uids))
			)
			await s.execute(
				sa.text("DELETE FROM django_session WHERE session_key LIKE 'port%'")
			)
			await s.execute(sa.delete(Account).where(Account.id.in_(uids)))
			await s.commit()

	ids = run_async(setup())
	yield ids
	run_async(teardown(ids))


@pytest.fixture
def port_client(port_users):
	"""Test client for the migrated /api surface -- real session auth,
	ninja-shaped error handlers, revision startup -- against the test DB."""
	from litestar import Router
	from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
	from litestar.testing import create_test_client

	from otodb_next import revisions
	from otodb_next.api.source import source_router
	from otodb_next.errors import exception_handlers
	from otodb_next.middleware import SessionAuthMiddleware

	config = SQLAlchemyAsyncConfig(
		connection_string=sa_url().render_as_string(hide_password=False),
		create_all=False,
	)
	with create_test_client(
		route_handlers=[Router(path='/api', route_handlers=[source_router])],
		middleware=[SessionAuthMiddleware],
		exception_handlers=exception_handlers,
		plugins=[SQLAlchemyPlugin(config=config)],
		on_startup=[revisions.load_content_types],
		backend_options={
			'loop_factory': lambda: asyncio.SelectorEventLoop(
				selectors.SelectSelector()
			)
		},
	) as client:
		yield client


def login(client, role: str):
	client.cookies.set('sessionid', f'port{role}')
	return client


def logout(client):
	client.cookies.clear()
	return client
