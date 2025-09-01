from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

from otodb.account.models import Account

from .enums import Status, RequestActions

class BulkRequest(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='bulk_requests', null=False)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.PENDING
    )

class UserRequest(models.Model):
    bulk = models.ForeignKey(BulkRequest, on_delete=models.CASCADE, related_name='requests', null=False)
    command = models.IntegerField(choices=RequestActions.choices)
    A_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='requests_A')
    A_id = models.PositiveBigIntegerField()
    B_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='requests_B')
    B_id = models.PositiveBigIntegerField()
    A = GenericForeignKey('A_type', 'A_id')
    B = GenericForeignKey('B_type', 'B_id')

    class Meta:
        unique_together = (("bulk", "command", "A_type", "A_id", "B_type", "B_id"),)

