"""Tests for the in-process job scheduler."""

import asyncio

from otodb_next.scheduler import Job, _tick


def test_lock_key_is_stable_int64():
	job = Job('moderation sweep', interval=60, run=lambda: None)
	assert job.lock_key == Job('moderation sweep', interval=1, run=print).lock_key
	assert Job('other job', interval=60, run=print).lock_key != job.lock_key
	assert -(2**63) <= job.lock_key < 2**63


class FakeResult:
	def __init__(self, value):
		self._value = value

	def scalar(self):
		return self._value


class FakeConnection:
	"""Grants the advisory lock (or not) and records executed statements."""

	def __init__(self, grant_lock):
		self.grant_lock = grant_lock
		self.statements = []

	async def execute(self, query, params=None):
		self.statements.append(str(query))
		return FakeResult(self.grant_lock)

	async def __aenter__(self):
		return self

	async def __aexit__(self, *exc):
		return False


class FakeEngine:
	def __init__(self, grant_lock=True):
		self.connection = FakeConnection(grant_lock)

	def connect(self):
		return self.connection


def test_tick_runs_job_and_unlocks_when_lock_granted():
	ran = []
	job = Job('t', interval=60, run=lambda: ran.append(1) or 'did a thing')
	engine = FakeEngine(grant_lock=True)
	asyncio.run(_tick(engine, job))
	assert ran == [1]
	assert any('pg_try_advisory_lock' in s for s in engine.connection.statements)
	assert any('pg_advisory_unlock' in s for s in engine.connection.statements)


def test_tick_skips_job_when_lock_not_granted():
	ran = []
	job = Job('t', interval=60, run=lambda: ran.append(1))
	engine = FakeEngine(grant_lock=False)
	asyncio.run(_tick(engine, job))
	assert ran == []
	assert not any('pg_advisory_unlock' in s for s in engine.connection.statements)
