from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_request_cache import get_request_cache
from dirtyfields import DirtyFieldsMixin

from otodb.account.models import Account


class Revision(models.Model):
	user = models.ForeignKey(Account, on_delete=models.PROTECT, null=False)
	date = models.DateTimeField(auto_now_add=True)
	message = models.TextField(null=False, default='')


class RevisionChange(models.Model):
	rev = models.ForeignKey(Revision, null=False, on_delete=models.CASCADE)

	target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
	target_id = models.PositiveBigIntegerField(null=False)
	target = GenericForeignKey('target_type', 'target_id')
	deleted = models.BooleanField(default=False, null=False)

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


class RevisionChangeEntity(models.Model):
	change = models.ForeignKey(RevisionChange, null=False, on_delete=models.CASCADE)
	entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
	entity_id = models.PositiveBigIntegerField(null=False)
	entity = GenericForeignKey('entity_type', 'entity_id')

	class Meta:
		unique_together = (
			(
				'change',
				'entity_type',
				'entity_id',
			),
		)


def get_serialized_value(instance: models.Model, field):
	field = instance._meta.get_field(field)
	return field.value_to_string(instance)  # type: ignore


def _bulk_get_new_rev(model, objs):
	all_changes = []

	for obj in objs:
		if obj.pk is None:
			continue
		changes = {}
		for k in obj.get_dirty_fields(check_relationship=True):
			if k in model.revision_tracked_fields:
				changes[k] = get_serialized_value(obj, k)
		all_changes.append(changes)

	return all_changes


def _get_ents(obj):
	return tuple(
		[
			getattr(obj if attr == 'self' else getattr(obj, attr), 'pk', None)
			for attr in type(obj).revision_entity_attrs
		]
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
		changed = 0
		for instance in self.all():
			for k, v in kwargs.items():
				setattr(instance, k, v)
			changed += instance.save()  # instance will make records
		return changed

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
