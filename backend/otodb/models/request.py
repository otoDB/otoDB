from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

from django.conf import settings

from .enums import Status, RequestActions


class BulkRequest(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='bulk_requests',
		null=False,
	)
	processed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='processed_requests',
		null=True,
	)
	status = models.IntegerField(choices=Status.choices, default=Status.PENDING)

	class Meta:
		constraints = [
			models.CheckConstraint(
				name='request_processed_by_notnull_iff_not_pending',
				condition=(
					models.Q(status=Status.PENDING)
					| models.Q(processed_by__isnull=False)
				)
				& (
					models.Q(processed_by__isnull=True)
					| ~models.Q(status=Status.PENDING)
				),
				violation_error_message='processed_by null <=> status is pending',
			),
		]


class UserRequest(models.Model):
	bulk = models.ForeignKey(
		BulkRequest, on_delete=models.CASCADE, related_name='requests', null=False
	)
	command = models.IntegerField(choices=RequestActions.choices)
	A_type = models.ForeignKey(
		ContentType, on_delete=models.CASCADE, related_name='requests_A'
	)
	A_id = models.PositiveBigIntegerField()
	B_type = models.ForeignKey(
		ContentType, on_delete=models.CASCADE, related_name='requests_B'
	)
	B_id = models.PositiveBigIntegerField()
	A = GenericForeignKey('A_type', 'A_id')
	B = GenericForeignKey('B_type', 'B_id')

	class Meta:
		unique_together = (('bulk', 'command', 'A_type', 'A_id', 'B_type', 'B_id'),)
