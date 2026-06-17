from datetime import timedelta

import pytest
from django.utils import timezone

from otodb.api.common import revision
from otodb.api.history import rollback_entity
from otodb.models import MediaWork, Revision, TagWork, TagWorkInstance


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
