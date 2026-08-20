"""Cascade deletes are captured by the DB triggers.

Under the old ORM capture this needed `_collect_cascade_deletions` because Django's
fast-delete path bypassed `save()`/`delete()`. With triggers it's automatic: Django's
on_delete=CASCADE issues real DELETE SQL on child tables, and each child's row-level
AFTER DELETE trigger records the deletion -- regardless of manager or fast-delete.

(The former base-manager-pinning test is gone: `RevisionTrackedQuerySet` no longer
exists, and capture no longer depends on which manager a write goes through.)
"""

import pytest
from django.contrib.contenttypes.models import ContentType

from otodb.models import Revision, RevisionChange, TagWork, TagWorkParenthood
from otodb.revision_db import db_revision


@pytest.mark.django_db
def test_cascade_delete_is_captured(member):
	parent = TagWork.objects.create(name='p1', slug='p1')
	child = TagWork.objects.create(name='c1', slug='c1')
	twp = TagWorkParenthood.objects.create(tag=child, parent=parent, primary=True)
	Revision.objects.all().delete()  # drop the setup revisions (CASCADE to changes)

	with db_revision(user=member):
		TagWork.objects.filter(pk=parent.pk).delete()

	tw_ct = ContentType.objects.get_for_model(TagWork).pk
	twp_ct = ContentType.objects.get_for_model(TagWorkParenthood).pk
	deleted = set(
		RevisionChange.objects.filter(deleted=True).values_list(
			'target_type_id', 'target_id'
		)
	)
	assert (tw_ct, parent.pk) in deleted
	assert (twp_ct, twp.pk) in deleted, (
		'cascade-deleted TagWorkParenthood was not captured by its trigger'
	)
