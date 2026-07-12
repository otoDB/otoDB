"""Write-parity harness for otodb_next.revisions: the same scenario executed
through the Django revision system and through the SQLAlchemy port must
produce identical revision/revisionchange/revisionchangeentity/subscription/
notification rows (modulo pks and timestamps, normalized to symbols).

The port side runs on its own connection inside a transaction that is always
rolled back -- Django's FK constraints are DEFERRABLE INITIALLY DEFERRED, so it
can reference rows from Django's (uncommitted) test transaction without ever
validating them.

ORDERING MATTERS: the port scenario must run BEFORE the Django scenario, and
the fixture tag is created untracked. Both sides insert identical unique keys
(the connection row, the auto-subscribe row); a unique-index check against a
row another OPEN transaction inserted blocks until that transaction ends, so
overlapping the two sides deadlocks the test. The port side finishes (and
rolls back) before Django writes; lock_timeout on the port engine turns any
future overlap into a loud failure instead of a hang.
"""

import pytest
import sqlalchemy as sa
from django.contrib.contenttypes.models import ContentType as DjContentType
from sqlalchemy.ext.asyncio import async_sessionmaker

from otodb.models import TagWork as DjTagWork
from otodb.models import TagWorkConnection as DjTagWorkConnection
from otodb.models.enums import Route
from otodb.models.posts import Notification as DjNotification
from otodb.models.posts import Subscription as DjSubscription
from otodb.models.revision import Revision as DjRevision
from otodb.revisions import revision as dj_revision
from otodb_next import revisions as port
from otodb_next.models import (
	ContentType,
	Notification,
	Revision,
	RevisionChange,
	RevisionChangeEntity,
	Subscription,
	TagWorkConnection,
)
from tests.otodb_next.conftest import run_async

MESSAGES = ('create', 'edit', 'delete')
ROUTE = int(Route.TAGWORK_EDIT_CONNECTIONS)


def normalize(revs, subs, notifs, ids):
	"""Symbolize side-specific pks/user ids so both sides are comparable.

	Row symbols are keyed by (content type, pk) -- bare pks collide across
	tables (independent sequences all starting at 1 in a fresh test DB).
	"""
	rows = {
		('tagworkconnection', ids['conn']): 'CONN',
		('tagwork', ids['tag']): 'TAG',
	}
	users = {ids['member']: 'EDITOR', ids['editor']: 'OTHER'}

	def value(val, column):
		if column == 'tag' and val is not None:
			return rows[('tagwork', int(val))]
		return val

	return {
		'revisions': {
			r['message']: {
				'user': users[r['user']],
				'changes': sorted(
					(
						{
							'ct': c['ct'],
							'target': rows[(c['ct'], c['target'])],
							'column': c['column'],
							'value': value(c['value'], c['column']),
							'deleted': c['deleted'],
							'restored': c['restored'],
							'entities': sorted(
								(ct, rows[(ct, eid)], route)
								for ct, eid, route in c['entities']
							),
						}
						for c in r['changes']
					),
					key=lambda c: (c['column'] or '', c['deleted']),
				),
			}
			for r in revs
		},
		'subscriptions': sorted((users[s], ct, rows[(ct, e)]) for s, ct, e in subs),
		'notifications': sorted((users[t], msg) for t, msg in notifs),
	}


def django_scenario(member, editor, tag):
	route = Route.TAGWORK_EDIT_CONNECTIONS
	with dj_revision(user=member, message='create', route=route):
		conn = DjTagWorkConnection.objects.create(tag=tag, site=6, content_id='abc')
	conn_pk = conn.pk

	ct_conn = DjContentType.objects.get_for_model(DjTagWorkConnection)
	DjSubscription.objects.create(
		subscriber=editor, entity_type=ct_conn, entity_id=conn_pk
	)

	with dj_revision(user=member, message='edit', route=route):
		conn.site = 7
		conn.content_id = 'def'
		conn.save()

	with dj_revision(user=member, message='delete', route=route):
		conn.delete()

	revs = []
	for rev in DjRevision.objects.filter(message__in=MESSAGES).order_by('id'):
		changes = []
		for ch in rev.revisionchange_set.order_by('id'):
			changes.append(
				{
					'ct': ch.target_type.model,
					'target': ch.target_id,
					'column': ch.target_column,
					'value': ch.target_value,
					'deleted': ch.deleted,
					'restored': ch.restored,
					'entities': [
						(e.entity_type.model, e.entity_id, e.route)
						for e in ch.revisionchangeentity_set.all()
					],
				}
			)
		revs.append({'message': rev.message, 'user': rev.user_id, 'changes': changes})

	subs = [
		(s.subscriber_id, s.entity_type.model, s.entity_id)
		for s in DjSubscription.objects.all()
	]
	notifs = [(n.target_id, n.revision.message) for n in DjNotification.objects.all()]
	return normalize(
		revs,
		subs,
		notifs,
		{'conn': conn_pk, 'tag': tag.pk, 'member': member.pk, 'editor': editor.pk},
	)


async def port_scenario(engine, member_id, editor_id, tag_id):
	async with async_sessionmaker(engine, expire_on_commit=False)() as s:
		await port.load_content_types(s)
		ct_names = {id_: model for model, id_ in await _ct_pairs(s)}
		ct_ids = {model: id_ for id_, model in ct_names.items()}

		async with port.revision_scope(
			s, user_id=member_id, message='create', route=ROUTE
		):
			conn = TagWorkConnection(tag_id=tag_id, site=6, content_id='abc')
			s.add(conn)
		conn_id = conn.id

		s.add(
			Subscription(
				subscriber_id=editor_id,
				entity_type_id=ct_ids['tagworkconnection'],
				entity_id=conn_id,
			)
		)
		await s.flush()

		async with port.revision_scope(
			s, user_id=member_id, message='edit', route=ROUTE
		):
			conn.site = 7
			conn.content_id = 'def'

		async with port.revision_scope(
			s, user_id=member_id, message='delete', route=ROUTE
		):
			await s.delete(conn)

		revs = []
		rev_rows = (
			await s.execute(
				sa.select(Revision)
				.where(Revision.message.in_(MESSAGES))
				.order_by(Revision.id)
			)
		).scalars()
		for rev in rev_rows:
			changes = []
			ch_rows = (
				await s.execute(
					sa.select(RevisionChange)
					.where(RevisionChange.rev_id == rev.id)
					.order_by(RevisionChange.id)
				)
			).scalars()
			for ch in ch_rows:
				ents = (
					await s.execute(
						sa.select(RevisionChangeEntity).where(
							RevisionChangeEntity.change_id == ch.id
						)
					)
				).scalars()
				changes.append(
					{
						'ct': ct_names[ch.target_type_id],
						'target': ch.target_id,
						'column': ch.target_column,
						'value': ch.target_value,
						'deleted': ch.deleted,
						'restored': ch.restored,
						'entities': [
							(ct_names[e.entity_type_id], e.entity_id, e.route)
							for e in ents
						],
					}
				)
			revs.append(
				{'message': rev.message, 'user': rev.user_id, 'changes': changes}
			)

		subs = [
			(row.subscriber_id, ct_names[row.entity_type_id], row.entity_id)
			for row in (await s.execute(sa.select(Subscription))).scalars()
		]
		notifs = [
			(row.target_id, rev_msg)
			for row, rev_msg in (
				await s.execute(
					sa.select(Notification, Revision.message).join(
						Revision, Notification.revision_id == Revision.id
					)
				)
			)
		]
		shape = normalize(
			revs,
			subs,
			notifs,
			{
				'conn': conn_id,
				'tag': tag_id,
				'member': member_id,
				'editor': editor_id,
			},
		)
		await s.rollback()
		return shape


async def _ct_pairs(s):
	return (await s.execute(sa.select(ContentType.model, ContentType.id))).all()


EXPECTED_ENTITIES = [('tagwork', 'TAG', ROUTE)]
EXPECTED_REVISIONS = {
	'create': {
		'user': 'EDITOR',
		'changes': [
			{
				'ct': 'tagworkconnection',
				'target': 'CONN',
				'column': 'content_id',
				'value': 'abc',
				'deleted': False,
				'restored': False,
				'entities': EXPECTED_ENTITIES,
			},
			{
				'ct': 'tagworkconnection',
				'target': 'CONN',
				'column': 'site',
				'value': '6',
				'deleted': False,
				'restored': False,
				'entities': EXPECTED_ENTITIES,
			},
			{
				'ct': 'tagworkconnection',
				'target': 'CONN',
				'column': 'tag',
				'value': 'TAG',
				'deleted': False,
				'restored': False,
				'entities': EXPECTED_ENTITIES,
			},
		],
	},
	'edit': {
		'user': 'EDITOR',
		'changes': [
			{
				'ct': 'tagworkconnection',
				'target': 'CONN',
				'column': 'content_id',
				'value': 'def',
				'deleted': False,
				'restored': False,
				'entities': EXPECTED_ENTITIES,
			},
			{
				'ct': 'tagworkconnection',
				'target': 'CONN',
				'column': 'site',
				'value': '7',
				'deleted': False,
				'restored': False,
				'entities': EXPECTED_ENTITIES,
			},
		],
	},
	'delete': {
		'user': 'EDITOR',
		'changes': [
			{
				'ct': 'tagworkconnection',
				'target': 'CONN',
				'column': None,
				'value': None,
				'deleted': True,
				'restored': False,
				'entities': EXPECTED_ENTITIES,
			},
		],
	},
}


async def _port_system_user(engine):
	async with async_sessionmaker(engine)() as s:
		return await port.system_user(s)


@pytest.mark.django_db
def test_system_user_matches_django(port_engine):
	"""port.system_user() resolves the same account as Account.get_system()."""
	from otodb.account.models import Account as DjAccount

	dj = DjAccount.get_system()
	uid, is_active = run_async(_port_system_user(port_engine))
	assert (uid, is_active) == (dj.pk, dj.is_active)
	assert is_active is False  # what excludes the bot from auto-subscribe


@pytest.mark.django_db
def test_write_parity(member, editor, port_engine):
	"""Same scenario through both stacks -> identical normalized rows."""
	# Untracked on purpose (no revision CM): a tracked create would
	# auto-subscribe member to the tag inside Django's open transaction --
	# the same unique key the port side inserts (see module docstring).
	tag = DjTagWork.objects.create(name='parity tag')

	# Port side FIRST -- it rolls back before Django writes the same keys.
	port_shape = run_async(port_scenario(port_engine, member.pk, editor.pk, tag.pk))
	django_shape = django_scenario(member, editor, tag)

	assert django_shape == port_shape

	# and both match the hand-written canonical expectation
	assert django_shape['revisions'] == EXPECTED_REVISIONS
	assert django_shape['subscriptions'] == [('EDITOR', 'tagwork', 'TAG')]
	assert django_shape['notifications'] == [('OTHER', 'edit')]
