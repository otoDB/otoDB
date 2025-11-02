from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_request_cache import get_request_cache
from dirtyfields import DirtyFieldsMixin

from otodb.account.models import Account
from otodb.models.enums import Route


class Revision(models.Model):
	user = models.ForeignKey(Account, on_delete=models.PROTECT, null=True)
	date = models.DateTimeField(auto_now_add=True)
	message = models.TextField(null=False, default='')

	@property
	def actions(self):
		return (
			RevisionChangeEntity.objects.filter(change__rev=self)
			.values('route', 'entity_type__model', 'entity_id')
			.distinct()
		)


class RevisionChange(models.Model):
	rev = models.ForeignKey(Revision, null=False, on_delete=models.CASCADE)

	target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
	target_id = models.PositiveBigIntegerField(null=False)
	target = GenericForeignKey('target_type', 'target_id')
	deleted = models.BooleanField(default=False, null=False)
	restored = models.BooleanField(default=False, null=False)

	target_column = models.CharField(max_length=100, null=True)
	target_value = models.TextField(null=True)

	class Meta:
		unique_together = (
			(
				'rev',
				'target_type',
				'target_id',
				'target_column',
			),
		)
		constraints = [
			models.CheckConstraint(
				check=~models.Q(deleted=True, restored=True),
				name='revisionchange_cannot_be_both_delete_and_restore',
			),
			models.UniqueConstraint(
				fields=['target_type', 'target_id'],
				condition=models.Q(deleted=True),
				name='revisionchange_model_can_only_be_deleted_once',
			),
			models.UniqueConstraint(
				fields=['target_type', 'target_id'],
				condition=models.Q(restored=True),
				name='revisionchange_model_can_only_be_restored_once',
			),
		]


class RevisionChangeEntity(models.Model):
	change = models.ForeignKey(RevisionChange, null=False, on_delete=models.CASCADE)
	entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
	entity_id = models.PositiveBigIntegerField(null=False)
	entity = GenericForeignKey('entity_type', 'entity_id')
	route = models.IntegerField(
		null=False, choices=Route.choices, default=Route.UNKNOWN
	)

	class Meta:
		unique_together = (
			(
				'change',
				'entity_type',
				'entity_id',
			),
		)


def get_serialized_value(instance: models.Model, field):
	field_obj = instance._meta.get_field(field)
	value = field_obj.value_from_object(instance)
	if value is None:
		return None
	return field_obj.value_to_string(instance)  # type: ignore


def _bulk_get_new_rev(model, objs):
	all_changes = []
	for obj in objs:
		changes = {}
		for k in obj.get_dirty_fields(check_relationship=True):
			if k in model.revision_tracked_fields:
				changes[k] = get_serialized_value(obj, k)
		all_changes.append(changes)

	return all_changes


def _get_ents(obj):
	return tuple(
		obj.pk if attr == 'self' else getattr(obj, obj._meta.get_field(attr).attname)
		for attr in type(obj).revision_entity_attrs
	)


class RevisionTrackedQuerySet(models.QuerySet):
	def bulk_create(self, objs, *args, **kwargs):
		all_changes = _bulk_get_new_rev(self.model, objs)
		cache = get_request_cache()
		rev = cache.get('rev')
		ctpk = ContentType.objects.get_for_model(self.model).pk
		objs = super().bulk_create(objs, *args, **kwargs)
		for changes, obj in zip(all_changes, objs):
			if obj.pk is not None:
				ents = _get_ents(obj)
				for k in changes:
					rev[(ctpk, obj.pk, k)] = ents, changes[k]
		cache.set('rev', rev)

		return objs

	def bulk_update(self, objs, *args, **kwargs):
		all_changes = _bulk_get_new_rev(self.model, objs)
		cache = get_request_cache()
		rev = cache.get('rev')
		ctpk = ContentType.objects.get_for_model(self.model).pk
		ret = super().bulk_update(objs, *args, **kwargs)
		for changes, obj in zip(all_changes, objs):
			if obj.pk is not None:
				ents = _get_ents(obj)
				for k in changes:
					rev[(ctpk, obj.pk, k)] = ents, changes[k]
		cache.set('rev', rev)

		return ret

	def update(self, **kwargs):
		# This seems bad but we need to record revisions anyway, so it's as good as it can be
		matched = 0
		for instance in self.all():
			for k, v in kwargs.items():
				setattr(instance, k, v)
			instance.save()
			matched += 1
		return matched

	def delete(self):
		to_del_dicts = self.all().values(
			'pk', *[x for x in self.model.revision_entity_attrs if x != 'self']
		)
		cache = get_request_cache()
		if cache is None:
			print(
				f'DELETING {[o["pk"] for o in to_del_dicts]} ON {self.model} --- NOT TRACKING CHANGES'
			)
		else:
			rev_del = cache.get('rev_del')
			ctpk = ContentType.objects.get_for_model(model=self.model).pk
			for obj in to_del_dicts:
				ents = tuple(
					[
						obj['pk' if attr == 'self' else attr]
						for attr in self.model.revision_entity_attrs
					]
				)
				rev_del.append(
					(
						ctpk,
						obj['pk'],
						ents,
					)
				)
		super().delete()
		if cache is not None:
			cache.set('rev_del', rev_del)
		return len(to_del_dicts)


class RevisionTrackedManager(models.Manager):
	def get_queryset(self):
		return RevisionTrackedQuerySet(self.model, using=self._db)


class RevisionTrackedModel(DirtyFieldsMixin, models.Model):
	revision_tracked_fields: list[str] = []
	revision_entity_attrs: list[str] = []

	objects = RevisionTrackedManager()

	class Meta:
		abstract = True

	def save(self, *args, **kwargs) -> bool:
		cache = get_request_cache()
		dirty = self.get_dirty_fields(check_relationship=True)
		# Needs to commit so we get a PK, but only after dirty fields have been copied
		super().save(*args, **kwargs)
		if cache is None:
			for k, v in dirty.items():
				if k in self.revision_tracked_fields:
					print(
						f'UPDATING {k}: {v} -> {getattr(self, k)} ON {self} ({type(self)}.{self.pk}) --- NOT TRACKING CHANGES'
					)
		else:
			rev = cache.get('rev')
			ctpk = ContentType.objects.get_for_model(model=type(self)).pk
			ents = _get_ents(self)
			for k in dirty:
				if k in self.revision_tracked_fields:
					rev[(ctpk, self.pk, k)] = ents, get_serialized_value(self, k)
			cache.set('rev', rev)
		return len(self.get_dirty_fields(check_relationship=True)) > 0

	def delete(self, *args, **kwargs):
		ents = _get_ents(self)
		pk = self.pk  # actually deleting will null the PK
		if ret := super().delete(*args, **kwargs):
			cache = get_request_cache()
			if cache is None:
				print(f'DELETING {self} ({type(self)}.{pk}) --- NOT TRACKING CHANGES')
			else:
				rev_del = cache.get('rev_del')

				rev_del.append(
					(
						ContentType.objects.get_for_model(model=type(self)).pk,
						pk,
						ents,
					)
				)
				cache.set('rev_del', rev_del)

			return ret
