import pytest
from django.contrib.contenttypes.models import ContentType
from django_request_cache import get_request_cache

from otodb.models import MediaWork, TagWork, TagWorkInstance, TagWorkParenthood


def _deleted_keys():
	return {(ctpk, pk) for ctpk, pk, _ in get_request_cache().get('rev_del')}


@pytest.mark.django_db
class TestCascadeDeletionTracking:
	"""When Django routes a tracked cascade child through its `fast_deletes`
	optimization, `_collect_cascade_deletions` must still record it.
	"""

	@pytest.fixture
	def force_fast_delete(self, monkeypatch):
		from django.db.models.deletion import Collector

		monkeypatch.setattr(
			Collector, '_has_signal_listeners', lambda self, model: False
		)

	def test_cascade_deletes_tracked_children_via_queryset(
		self, member, force_fast_delete
	):
		parent = TagWork.objects.create(name='p1', slug='p1')
		child = TagWork.objects.create(name='c1', slug='c1')
		twp = TagWorkParenthood.objects.create(tag=child, parent=parent, primary=True)

		get_request_cache().set('rev_del', [])
		TagWork.objects.filter(pk=parent.pk).delete()

		tw_ct = ContentType.objects.get_for_model(TagWork).pk
		twp_ct = ContentType.objects.get_for_model(TagWorkParenthood).pk
		assert (tw_ct, parent.pk) in _deleted_keys()
		assert (twp_ct, twp.pk) in _deleted_keys(), (
			'TagWorkParenthood cascade was not tracked; Django fast-deleted it '
			'and _collect_cascade_deletions missed the fast_deletes bucket'
		)

	def test_cascade_deletes_tracked_children_via_instance(
		self, member, force_fast_delete
	):
		parent = TagWork.objects.create(name='p2', slug='p2')
		child = TagWork.objects.create(name='c2', slug='c2')
		twp = TagWorkParenthood.objects.create(tag=child, parent=parent, primary=True)

		get_request_cache().set('rev_del', [])
		parent.delete()

		twp_ct = ContentType.objects.get_for_model(TagWorkParenthood).pk
		assert (twp_ct, twp.pk) in _deleted_keys()


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
