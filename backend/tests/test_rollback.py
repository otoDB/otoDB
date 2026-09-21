from datetime import timedelta

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.utils import timezone

from otodb.api.common import revision
from otodb.api.history import get_rev_restored, rollback_entity
from otodb.models import (
	MediaWork,
	Revision,
	RevisionChange,
	TagWork,
	TagWorkInstance,
	WorkSource,
)
from otodb.models.enums import Platform, WorkOrigin, WorkStatus
from otodb.models.posts import Subscription


def _set_date(rev_id, when):
	# date is auto_now_add, so bypass it with a direct UPDATE.
	Revision.objects.filter(id=rev_id).update(date=when)


@pytest.mark.django_db
class TestRollbackRestoredRows:
	"""A child row restored by one rollback must survive a later rollback that
	targets an earlier date.

	Regression for the bug where rolling back vandalism revisions newest->oldest
	deleted tags that an earlier rollback had just restored: the restored row has
	no revision history before the earlier cutoff, so the "modified entity" branch
	wrongly treated it as created-after-cutoff and deleted it.
	"""

	def test_second_earlier_rollback_keeps_restored_child(self, member):
		now = timezone.now()
		# Controlled, distinct revision dates so the rollback's date comparisons are
		# deterministic. The two rollbacks themselves get real (later) timestamps.
		t_a = now - timedelta(seconds=300)
		t_b = now - timedelta(seconds=200)
		t_c = now - timedelta(seconds=100)

		# rev A: create the work, a tag, and the tag instance linking them.
		with revision(user=member, message='create'):
			work = MediaWork.objects.create(title='W', description='d0', rating=0)
			tag = TagWork.objects.create(name='t', slug='t')
			TagWorkInstance.objects.create(work=work, work_tag=tag)
		_set_date(Revision.objects.latest('id').id, t_a)

		# rev B (later): edit the work's description (analog of the earlier vandalism rev).
		with revision(user=member, message='edit description'):
			work.refresh_from_db()
			work.description = 'd1'
			work.save()
		_set_date(Revision.objects.latest('id').id, t_b)

		# rev C (later still): delete the tag instance (analog of the tag-removal rev).
		with revision(user=member, message='delete tag'):
			TagWorkInstance.objects.filter(work=work, work_tag=tag).delete()
		_set_date(Revision.objects.latest('id').id, t_c)

		assert not TagWorkInstance.objects.filter(work=work, work_tag=tag).exists()

		# First rollback (newest): undo rev C -> the tag instance is restored as a new row.
		with revision(user=member, message='rollback C'):
			rollback_entity(work.pk, 'mediawork', t_c)
		assert TagWorkInstance.objects.filter(work=work, work_tag=tag).exists(), (
			'first rollback should restore the deleted tag instance'
		)

		# Second rollback (older): undo rev B. This re-processes the work and must NOT
		# delete the just-restored tag instance.
		with revision(user=member, message='rollback B'):
			rollback_entity(work.pk, 'mediawork', t_b)

		assert TagWorkInstance.objects.filter(work=work, work_tag=tag).count() == 1, (
			'restored tag instance was deleted by the earlier-dated rollback'
		)


@pytest.mark.django_db
class TestRollbackRestoreChain:
	"""When a row has been deleted-and-restored more than once, rolling back into a
	middle generation's lifetime must read that generation's history -- not an older
	generation's. Resolving a restored row to its origin must stop at the generation
	that was already alive at the rollback date, otherwise a stale value is restored.
	"""

	def _live(self, work, tag):
		return TagWorkInstance.objects.get(work=work, work_tag=tag)

	def test_rollback_into_intermediate_generation(self, member):
		now = timezone.now()
		t0 = now - timedelta(seconds=1000)  # create, creator_roles=1
		t1 = now - timedelta(seconds=900)  # creator_roles=2
		t2 = now - timedelta(seconds=800)  # delete (gen1)
		t3 = now - timedelta(seconds=700)  # restore -> gen2 (creator_roles=2)
		t4 = now - timedelta(seconds=600)  # gen2 creator_roles=3
		t5 = now - timedelta(seconds=500)  # delete (gen2)
		t6 = now - timedelta(seconds=400)  # restore -> gen3 (creator_roles=3)
		# Between t4 and t5: gen2 is the live row, with its edited creator_roles=3.
		cutoff = now - timedelta(seconds=550)

		with revision(user=member, message='create'):
			work = MediaWork.objects.create(title='W', description='d', rating=0)
			tag = TagWork.objects.create(name='t', slug='t')
			TagWorkInstance.objects.create(work=work, work_tag=tag, creator_roles=1)
		_set_date(Revision.objects.latest('id').id, t0)

		with revision(user=member, message='roles=2'):
			twi = self._live(work, tag)
			twi.creator_roles = 2
			twi.save()
		_set_date(Revision.objects.latest('id').id, t1)

		with revision(user=member, message='delete gen1'):
			self._live(work, tag).delete()
		_set_date(Revision.objects.latest('id').id, t2)

		with revision(user=member, message='restore -> gen2'):
			rollback_entity(work.pk, 'mediawork', t2)
		_set_date(Revision.objects.latest('id').id, t3)
		assert self._live(work, tag).creator_roles == 2

		with revision(user=member, message='gen2 roles=3'):
			twi = self._live(work, tag)
			twi.creator_roles = 3
			twi.save()
		_set_date(Revision.objects.latest('id').id, t4)

		with revision(user=member, message='delete gen2'):
			self._live(work, tag).delete()
		_set_date(Revision.objects.latest('id').id, t5)

		with revision(user=member, message='restore -> gen3'):
			rollback_entity(work.pk, 'mediawork', t5)
		_set_date(Revision.objects.latest('id').id, t6)
		assert self._live(work, tag).creator_roles == 3

		# Roll back to a date when gen2 was live (after its creator_roles=3 edit).
		# The value 3 lives only in gen2's history -- not in the original generation,
		# which only ever reached 2.
		with revision(user=member, message='rollback into gen2 window'):
			rollback_entity(work.pk, 'mediawork', cutoff)

		roles = self._live(work, tag).creator_roles
		assert roles == 3, (
			f'expected gen2 edited value 3, got {roles} '
			'(resolved back to a stale older generation)'
		)


@pytest.mark.django_db
class TestRollbackRestoresDeletedTag:
	"""Rolling back a work whose tag was also deleted must restore the tag too.

	Regression for two Postgres-only failures hit while restoring a deleted TagWork:
	  1. update_or_create on TagWork ran its internal select_for_update() over the
	     manager's select_related('aliased_to') outer join, which Postgres rejects
	     with "FOR UPDATE cannot be applied to the nullable side of an outer join".
	  2. the related-target fix-up then resolved to_active against the tag's stale
	     pre-delete pk, raising TagWork.DoesNotExist because the tag had just been
	     restored under a new pk.
	"""

	def test_rollback_restores_deleted_tag_and_relinks_instance(self, member):
		now = timezone.now()
		t_create = now - timedelta(seconds=300)
		t_delete = now - timedelta(seconds=200)
		cutoff = now - timedelta(seconds=250)  # between create and delete

		# rev A: create the work, a tag, and the instance linking them.
		with revision(user=member, message='create'):
			work = MediaWork.objects.create(title='W', description='d', rating=0)
			tag = TagWork.objects.create(name='t', slug='t')
			TagWorkInstance.objects.create(work=work, work_tag=tag)
		_set_date(Revision.objects.latest('id').id, t_create)

		# rev B: delete the instance and the tag itself.
		with revision(user=member, message='delete instance and tag'):
			TagWorkInstance.objects.filter(work=work, work_tag=tag).delete()
			tag.delete()
		_set_date(Revision.objects.latest('id').id, t_delete)

		assert not TagWork.objects.filter(slug='t').exists()
		assert not TagWorkInstance.objects.filter(work=work).exists()

		# Roll the work back to before the deletion. Restoring the deleted instance
		# must recursively restore the deleted tag (exercising both fixes) and the
		# restored instance must point at the restored tag.
		with revision(user=member, message='rollback'):
			rollback_entity(work.pk, 'mediawork', cutoff)

		restored_tag = TagWork.objects.get(slug='t')
		instance = TagWorkInstance.objects.get(work=work)
		assert instance.work_tag_id == restored_tag.id


@pytest.mark.django_db
class TestRollbackAliasedTagDuplicate:
	"""Restoring a deleted tag instance whose tag has since been aliased into a
	tag the work already carries must not blow up on the (work, work_tag) unique
	constraint.

	The second-pass FK fix-up runs to_active on the restored instance's work_tag,
	resolving the aliased tag to its alias target -- a tag the work already has --
	so a naive UPDATE collides on otodb_tagworkinstance's unique constraint. The
	redundant restored row should be dropped instead.
	"""

	def test_rollback_restored_instance_resolving_to_existing_tag(self, member):
		now = timezone.now()
		t_create = now - timedelta(seconds=300)  # work tagged with both A and B
		t_remove = now - timedelta(seconds=200)  # remove A from the work
		t_alias = now - timedelta(seconds=100)  # alias A -> B
		cutoff = now - timedelta(seconds=250)  # between create and remove

		# rev A: the work carries both tag A and tag B.
		with revision(user=member, message='create'):
			work = MediaWork.objects.create(title='W', description='d', rating=0)
			tag_a = TagWork.objects.create(name='a', slug='a')
			tag_b = TagWork.objects.create(name='b', slug='b')
			TagWorkInstance.objects.create(work=work, work_tag=tag_a)
			TagWorkInstance.objects.create(work=work, work_tag=tag_b)
		_set_date(Revision.objects.latest('id').id, t_create)

		# rev B: remove tag A from the work (deletes that instance).
		removed_pk = TagWorkInstance.objects.get(work=work, work_tag=tag_a).pk
		with revision(user=member, message='remove a'):
			TagWorkInstance.objects.filter(work=work, work_tag=tag_a).delete()
		_set_date(Revision.objects.latest('id').id, t_remove)

		# rev C: alias A into B. A separate, later revision so rolling the work
		# back to `cutoff` never resets the alias -- to_active(A) stays B.
		with revision(user=member, message='alias a -> b'):
			tag_a.refresh_from_db()
			tag_a.aliased_to = tag_b
			tag_a.save()
		_set_date(Revision.objects.latest('id').id, t_alias)

		# Roll the work back to before A was removed. The restored A-instance's
		# work_tag resolves through to_active to B, which the work already has, so
		# the restore must not raise an IntegrityError.
		with revision(user=member, message='rollback'):
			rollback_entity(work.pk, 'mediawork', cutoff)

		# The redundant restored row is dropped; the pre-existing B instance stays.
		instances = TagWorkInstance.objects.filter(work=work)
		assert instances.count() == 1
		assert instances.get().work_tag_id == tag_b.id

		# At COMMIT the restore that was taken back leaves no trace: the short-lived row
		# was created and deleted in the rollback's Revision, so finalize erases it together
		# with its restored-marker -- and the Revision, which changed nothing, goes too.
		connection.check_constraints()  # fires the deferred finalize, as COMMIT would
		instance_ct = ContentType.objects.get_for_model(TagWorkInstance).id
		assert get_rev_restored(instance_ct, removed_pk) is None
		assert not RevisionChange.objects.filter(
			target_type_id=instance_ct, restored=True
		).exists()
		assert not Revision.objects.filter(message='rollback').exists()


@pytest.mark.django_db
class TestRollbackWriteOrder:
	"""Two overlapping transactions can write a row in the opposite order to their
	Revisions' dates (a Revision is dated by its transaction's start). What a rollback
	restores is the value last WRITTEN before the cutoff -- the latest change row by
	change id -- not the one whose Revision carries the latest date.
	"""

	def test_restores_last_written_value(self, member):
		now = timezone.now()
		t_create = now - timedelta(seconds=400)
		t_started_first = now - timedelta(seconds=300)
		t_started_second = now - timedelta(seconds=200)
		t_vandalism = now - timedelta(seconds=100)

		with revision(user=member, message='create'):
			work = MediaWork.objects.create(title='W', description='d0', rating=0)
		_set_date(Revision.objects.latest('id').id, t_create)

		for description, when in (
			('started second, wrote first', t_started_second),
			('started first, wrote second', t_started_first),
			('vandalism', t_vandalism),
		):
			with revision(user=member, message=description):
				MediaWork.objects.filter(pk=work.pk).update(description=description)
			_set_date(Revision.objects.latest('id').id, when)

		with revision(user=member, message='rollback vandalism'):
			rollback_entity(work.pk, 'mediawork', t_vandalism)

		work.refresh_from_db()
		assert work.description == 'started first, wrote second'


@pytest.mark.django_db
class TestRollbackSubscriptions:
	"""A rollback restores a deleted work's source while it still points at the work's old
	id, and only afterwards re-points it at the restored work -- so the rollback's Revision
	is routed to both ids. The moderator is auto-subscribed to the restored work only: a
	subscription to the old, deleted id is one nothing would ever drop.
	"""

	def test_moderator_is_not_subscribed_to_the_deleted_id(self, member, editor):
		now = timezone.now()
		with revision(user=editor, message='create'):
			work = MediaWork.objects.create(title='W', description='d', rating=0)
			WorkSource.objects.create(
				added_by=editor,
				media=work,
				platform=Platform.YOUTUBE,
				url='https://www.youtube.com/watch?v=sub',
				source_id='sub',
				work_origin=WorkOrigin.AUTHOR,
				work_status=WorkStatus.AVAILABLE,
			)
		_set_date(Revision.objects.latest('id').id, now - timedelta(seconds=300))
		deleted_pk = work.pk

		with revision(user=editor, message='delete work'):
			work.delete()  # cascades to the source
		_set_date(Revision.objects.latest('id').id, now - timedelta(seconds=200))

		with revision(user=member, message='rollback'):
			rollback_entity(deleted_pk, 'mediawork', now - timedelta(seconds=250))
		connection.check_constraints()  # fires the deferred finalize, as COMMIT would

		restored = MediaWork.objects.get()
		assert WorkSource.objects.get().media_id == restored.pk != deleted_pk
		work_ct = ContentType.objects.get_for_model(MediaWork).id
		assert list(
			Subscription.objects.filter(
				subscriber=member, entity_type_id=work_ct
			).values_list('entity_id', flat=True)
		) == [restored.pk]
