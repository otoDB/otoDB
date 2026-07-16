from __future__ import annotations

import asyncio
import contextlib
import hashlib
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import text

if TYPE_CHECKING:
	from collections.abc import AsyncIterator, Callable, Sequence

	from litestar import Litestar
	from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


@dataclass
class Job:
	name: str
	interval: float  # seconds between runs; first run happens at startup
	run: Callable[[], object]  # sync callable, executed in a worker thread

	@property
	def lock_key(self) -> int:
		return int.from_bytes(
			hashlib.blake2b(self.name.encode(), digest_size=8).digest(), signed=True
		)


def _run_with_connection_cleanup(job: Job) -> object:
	from django.db import close_old_connections

	close_old_connections()
	try:
		return job.run()
	finally:
		close_old_connections()


async def _tick(engine: AsyncEngine, job: Job) -> None:
	async with engine.connect() as db:
		locked = (
			await db.execute(
				text('SELECT pg_try_advisory_lock(:key)'), {'key': job.lock_key}
			)
		).scalar()
		if not locked:
			return
		try:
			result = await asyncio.to_thread(_run_with_connection_cleanup, job)
			if result:
				logger.info('%s: %s', job.name, result)
		finally:
			await db.execute(
				text('SELECT pg_advisory_unlock(:key)'), {'key': job.lock_key}
			)


async def _loop(engine: AsyncEngine, job: Job) -> None:
	while True:
		try:
			await _tick(engine, job)
		except Exception:
			logger.exception('%s failed', job.name)
		await asyncio.sleep(job.interval)


def scheduler(jobs: Sequence[Job], get_engine: Callable[[], AsyncEngine]):
	"""Build a Litestar lifespan context manager running the given jobs."""

	@contextlib.asynccontextmanager
	async def lifespan(app: Litestar) -> AsyncIterator[None]:
		engine = get_engine()
		tasks = []
		if engine.dialect.name == 'postgresql':
			tasks = [asyncio.create_task(_loop(engine, job)) for job in jobs]
		try:
			yield
		finally:
			for task in tasks:
				task.cancel()
			for task in tasks:
				with contextlib.suppress(asyncio.CancelledError):
					await task

	return lifespan
