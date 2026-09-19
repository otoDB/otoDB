"""Tests for GET /api/stats/works/history endpoint."""

import datetime

import psycopg
import pytest
from django.db import connection
from litestar import Router
from litestar.plugins.sqlalchemy import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.testing import create_test_client

from otodb.models.enums import Status
from otodb_next.app import work_history


def _dsn() -> str:
	s = connection.settings_dict
	return (
		f'host={s["HOST"]} port={s["PORT"]} dbname={s["NAME"]}'
		f' user={s["USER"]} password={s["PASSWORD"]}'
	)


@pytest.fixture
def client(db):
	"""The endpoint, connected to the pytest database.

	The app builds its engine from settings at import time, so that engine points
	at the development database. The test supplies its own engine. Its session
	runs in Asia/Tokyo on purpose: the query must pin the UTC day boundary itself.
	"""
	s = connection.settings_dict
	config = SQLAlchemyAsyncConfig(
		connection_string=(
			f'postgresql+psycopg://{s["USER"]}:{s["PASSWORD"]}'
			f'@{s["HOST"]}:{s["PORT"]}/{s["NAME"]}'
			'?options=-c%20timezone%3DAsia/Tokyo'
		),
		create_all=False,
	)
	with create_test_client(
		route_handlers=[Router(path='/api', route_handlers=[work_history])],
		plugins=[SQLAlchemyPlugin(config)],
	) as client:
		yield client


@pytest.fixture
def works(db):
	"""Committed works, inserted with plain psycopg.

	The endpoint reads on its own connection and cannot see rows inside the test
	transaction. The fixture commits the rows and deletes them again by hand.
	This avoids `transactional_db`, whose truncation breaks the tests that follow.
	"""
	with psycopg.connect(_dsn(), autocommit=True) as conn:

		def work(created_at: str, moved_to: int | None = None) -> int:
			row = conn.execute(
				'INSERT INTO otodb_mediawork (rating, status, created_at, moved_to_id)'
				' VALUES (0, %s, %s, %s) RETURNING id',
				(
					Status.APPROVED,
					datetime.datetime.fromisoformat(created_at),
					moved_to,
				),
			).fetchone()
			return row[0]

		kept = work('2026-03-01T01:00:00+00:00')
		work('2026-03-01T22:00:00+00:00')
		work('2026-03-03T23:30:00+00:00')
		work('2026-03-04T00:30:00+00:00')
		work('2026-03-06T12:00:00+00:00', moved_to=kept)
	yield
	with psycopg.connect(_dsn(), autocommit=True) as conn:
		conn.execute('DELETE FROM otodb_mediawork')


def test_returns_the_running_total_for_each_day_that_gained_works(client, works):
	response = client.get('/api/stats/works/history')

	assert response.status_code == 200
	# The 2nd and the 5th gained no works, so they get no point. In Asia/Tokyo the
	# works of the 3rd and the 4th fall on one day, but the UTC cut keeps them
	# apart. The work that was merged into another work never appears.
	assert response.json() == [
		{'date': '2026-03-01', 'total': 2},
		{'date': '2026-03-03', 'total': 3},
		{'date': '2026-03-04', 'total': 4},
	]


def test_returns_an_empty_series_when_no_works_exist(client):
	response = client.get('/api/stats/works/history')

	assert response.status_code == 200
	assert response.json() == []
