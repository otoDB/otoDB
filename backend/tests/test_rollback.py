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
