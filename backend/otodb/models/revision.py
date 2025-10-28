from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_request_cache import get_request_cache
from dirtyfields import DirtyFieldsMixin

from otodb.account.models import Account


class Revision(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(null=False)

class RevisionChange(models.Model):
    rev = models.ForeignKey(Revision, null=False, on_delete=models.CASCADE)

    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, related_name='model_revision_changes')
    target_id = models.PositiveBigIntegerField(null=False)
    target = GenericForeignKey('target_type', 'target_id')
    deleted = models.BooleanField(default=False, null=False)

    target_column = models.CharField(max_length=100, null=False)
    target_value = models.TextField(null=False)

    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, related_name='entity_revision_changes')
    entity_id = models.PositiveBigIntegerField(null=False)
    entity = GenericForeignKey('entity_type', 'entity_id')

    class Meta:
        unique_together = (('rev', 'target_type', 'target_id', 'target_column',),)

class RevisionTrackedQuerySet(models.QuerySet):
    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError(
            "bulk_create is disabled; use instance.save() to ensure revision tracking."
        )

    def bulk_update(self, *args, **kwargs):
        raise NotImplementedError(
            "bulk_update is disabled; use instance.save() to ensure revision tracking."
        )

    def update(self, **kwargs):
        # This seems bad but we need to record revisions anyway, so it's as good as it can be
        changed = 0
        for instance in self.all():
            for k, v in kwargs.items():
                setattr(instance, k, v)
            changed += instance.save() # instance will make records
        return changed

    def delete(self):
        to_del = self.all().values_list('pk', flat=True)
        cache = get_request_cache()
        if cache is None:
            print(f"DELETING {to_del} ON {self.model} --- NOT TRACKING CHANGES")
        else:
            rev_del = cache.get('rev_del')
            for pk in to_del:
                rev_del.append((ContentType.objects.get_for_model(model=self.model).pk, pk))
        super().delete()
        return len(to_del)

class RevisionTrackedManager(models.Manager):
    def get_queryset(self):
        return RevisionTrackedQuerySet(self.model, using=self._db)

class RevisionTrackedModel(DirtyFieldsMixin, models.Model):
    revision_tracked_fields: list[str] = []

    objects = RevisionTrackedManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        cache = get_request_cache()
        if cache is None:
            for k, v in self.get_dirty_fields().items():
                if k in self.revision_tracked_fields:
                    print(f"UPDATING {k}: {v} -> {getattr(self, k)} ON {self} ({type(self)}.{self.pk}) --- NOT TRACKING CHANGES")
        else:
            rev = cache.get('rev')
            for k in self.get_dirty_fields():
                if k in self.revision_tracked_fields:
                    rev[(ContentType.objects.get_for_model(model=type(self)).pk, self.pk, k)] = getattr(self, k)
        super().save(*args, **kwargs)
        return len(self.get_dirty_fields()) > 0

    def delete(self, *args, **kwargs):
        if ret := super().delete(*args, **kwargs):
            cache = get_request_cache()
            if cache is None:
                print(f"DELETING {self} ({type(self)}.{self.pk}) --- NOT TRACKING CHANGES")
            else:
                rev_del = cache.get('rev_del')
                rev_del.append((ContentType.objects.get_for_model(model=type(self)).pk, self.pk))
            
            return ret
