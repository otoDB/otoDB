import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker

from otodb_next.enums import ErrorCode, Platform, Status, WorkOrigin, WorkStatus
from otodb_next.models import (
	MediaWork,
	Revision,
	RevisionChange,
	Subscription,
	WorkSource,
)
from tests.otodb_next.conftest import login, logout, run_async


@pytest.fixture
def source(port_engine, port_users):
	"""A committed PENDING work with one source; cleaned up afterwards."""
	Session = async_sessionmaker(port_engine, expire_on_commit=False)

	async def setup():
		async with Session() as s:
			work = MediaWork(rating=0, status=Status.PENDING, created_at=sa.func.now())
			s.add(work)
			await s.flush()
			src = WorkSource(
				media_id=work.id,
				platform=Platform.YOUTUBE,
				url='https://example.invalid/port-origin-test',
				work_origin=WorkOrigin.AUTHOR,
				work_status=WorkStatus.AVAILABLE,
				added_by_id=port_users['member'],
				is_pending=False,
				created_at=sa.func.now(),
			)
			s.add(src)
			await s.commit()
			return {'work': work.id, 'src': src.id}

	async def teardown(ids):
		async with Session() as s:
			await s.execute(
				sa.delete(WorkSource).where(WorkSource.id == ids['src']),
				execution_options={'revision_exempt': True},
			)
			await s.execute(sa.delete(MediaWork).where(MediaWork.id == ids['work']))
			await s.commit()

	ids = run_async(setup())
	yield ids
	run_async(teardown(ids))


async def _db_state(engine, ids, user_ids):
	async with async_sessionmaker(engine)() as s:
		origin = await s.scalar(
			sa.select(WorkSource.work_origin).where(WorkSource.id == ids['src'])
		)
		changes = (
			await s.execute(
				sa.select(
					Revision.user_id,
					RevisionChange.target_column,
					RevisionChange.target_value,
				)
				.join(RevisionChange, RevisionChange.rev_id == Revision.id)
				.where(Revision.user_id.in_(user_ids))
				.order_by(Revision.id)
			)
		).all()
		subs = (
			await s.execute(
				sa.select(Subscription.subscriber_id, Subscription.entity_id).where(
					Subscription.subscriber_id.in_(user_ids)
				)
			)
		).all()
	return origin, [tuple(c) for c in changes], sorted(tuple(x) for x in subs)


def _set_work_status(engine, work_id, status):
	async def flip():
		async with async_sessionmaker(engine)() as s:
			await s.execute(
				sa.update(MediaWork)
				.where(MediaWork.id == work_id)
				.values(status=status)
			)
			await s.commit()

	run_async(flip())


def test_source_origin_endpoint(port_client, port_users, port_engine, source):
	url = f'/api/upload/origin?source_id={source["src"]}&status=1'

	assert (r := logout(port_client).put(url)).status_code == 401
	assert r.json() == {'detail': 'Unauthorized'}

	assert (r := login(port_client, 'restricted').put(url)).status_code == 403
	assert r.json() == {'detail': 'Forbidden'}

	login(port_client, 'member')
	r = port_client.put('/api/upload/origin?source_id=999999999&status=1')
	assert (r.status_code, r.json()) == (404, {'detail': 'Not Found'})

	# happy path: work is PENDING, member (trusted) may edit
	assert port_client.put(url).status_code == 200

	# approved work -> member is rejected with the ApiError shape...
	_set_work_status(port_engine, source['work'], Status.APPROVED)
	r = port_client.put(url)
	assert (r.status_code, r.json()) == (403, {'code': ErrorCode.EDITOR_ONLY})

	# ...but an editor may still edit
	r = login(port_client, 'editor').put(
		f'/api/upload/origin?source_id={source["src"]}&status=0'
	)
	assert r.status_code == 200

	origin, changes, subs = run_async(
		_db_state(port_engine, source, list(port_users.values()))
	)
	member, editor = port_users['member'], port_users['editor']
	assert origin == 0  # the editor flipped it back
	assert changes == [
		(member, 'work_origin', '1'),
		(editor, 'work_origin', '0'),
	]
	# auto-subscribe on both routed entities; the editor's edit
	# notified-and-unsubscribed the member from the changed row (Django
	# commit-path parity), so the member keeps only the work subscription
	assert subs == sorted(
		[
			(member, source['work']),
			(editor, source['work']),
			(editor, source['src']),
		]
	)
