from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from otodb.account.models import Account


class Revision(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True)

class RevisionChange(models.Model):
    rev = models.ForeignKey(Revision, null=False)
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
    target_id = models.PositiveBigIntegerField(null=False)
    target = GenericForeignKey('target_type', 'target_id')
    target_column = models.CharField(max_length=100, null=False)
    target_value = models.TextField(null=False)

    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False)
    entity_id = models.PositiveBigIntegerField(null=False)
    entity = GenericForeignKey('entity_type', 'entity_id')

    class Meta:
        unique_together = (('rev', 'target_type', 'target_id', 'target_column',),)
