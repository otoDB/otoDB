import pytest
from django.contrib.contenttypes.models import ContentType
from django_request_cache import get_request_cache

from otodb.models import MediaWork, TagWork, TagWorkInstance, TagWorkParenthood


def _deleted_keys():
	return {(ctpk, pk) for ctpk, pk, _ in get_request_cache().get('rev_del')}


@pytest.mark.django_db
class TestCascadeDeletionTracking:
	"""Deleting a tracked parent must record every tracked cascade child in rev_del,
	even when Django routes them through its `fast_deletes` optimization path."""

	def test_cascade_deletes_tracked_children_via_queryset(self, member):
		work = MediaWork.objects.create(title='x', description='', rating=0)
		tag = TagWork.objects.create(name='t1', slug='t1')
		twi = TagWorkInstance.objects.create(work=work, work_tag=tag)

		get_request_cache().set('rev_del', [])
		MediaWork.objects.filter(pk=work.pk).delete()

		mw_ct = ContentType.objects.get_for_model(MediaWork).pk
		twi_ct = ContentType.objects.get_for_model(TagWorkInstance).pk
		assert (mw_ct, work.pk) in _deleted_keys()
		assert (twi_ct, twi.pk) in _deleted_keys(), (
			'TagWorkInstance cascade was not tracked'
		)

	def test_cascade_deletes_tracked_children_via_instance(self, member):
		work = MediaWork.objects.create(title='x2', description='', rating=0)
		tag = TagWork.objects.create(name='t2', slug='t2')
		twi = TagWorkInstance.objects.create(work=work, work_tag=tag)

		get_request_cache().set('rev_del', [])
		work.delete()

		twi_ct = ContentType.objects.get_for_model(TagWorkInstance).pk
		assert (twi_ct, twi.pk) in _deleted_keys()


@pytest.mark.django_db
class TestBaseManagerPinning:
	"""Django's _base_manager is used by Collector.related_objects, reverse
	relation descriptors, and third-party libs. Its queryset's .delete() must
	route through our RevisionTrackedQuerySet. Otherwise, .delete() on
	_base_manager querysets produces ghost rows."""

	@pytest.mark.parametrize(
		'model',
		[MediaWork, TagWork, TagWorkInstance, TagWorkParenthood],
	)
	def test_base_manager_queryset_delete_is_tracked(self, model):
		from otodb.models.revision import RevisionTrackedQuerySet

		qs_cls = type(model._base_manager.all())
		tracked = any(
			c.__dict__.get('delete') is RevisionTrackedQuerySet.__dict__['delete']
			for c in qs_cls.__mro__
		)
		assert tracked, (
			f'{model.__name__}._base_manager produces {qs_cls.__name__} whose '
			'.delete() does not route through RevisionTrackedQuerySet. '
			'Any cascade or third-party path using _base_manager.delete() will '
			'silently bypass revision tracking'
		)
