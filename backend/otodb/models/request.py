from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

from otodb.account.models import Account


class BulkRequest(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='bulk_requests', null=False)

class Request(models.Model):
    bulk = models.ForeignKey(BulkRequest, on_delete=models.CASCADE, related_name='prefs', null=False)
    command = models.IntegerField(BulkRequest)
    A_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    A_id = models.PositiveBigIntegerField()
    B_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    B_id = models.PositiveBigIntegerField()
    A = GenericForeignKey('A_type', 'A_id')
    B = GenericForeignKey('B_type', 'B_id')

    class Meta:
        unique_together = (("bulk", "command", "A_type", "A_id"),)

