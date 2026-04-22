from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.db.models import Q

from .enums import FlagStatus, ModerationEventType


class ModerationEvent(models.Model):
	if TYPE_CHECKING:
		work_id: int | None
		source_id: int | None
		by_id: int

	event_type = models.IntegerField(choices=ModerationEventType.choices)
	work = models.ForeignKey(
		'MediaWork',
		null=True,
		blank=True,
		on_delete=models.CASCADE,
		related_name='moderation_events',
	)
	source = models.ForeignKey(
		'WorkSource',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='moderation_events',
	)
	by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
	reason = models.CharField(max_length=1000, blank=True, default='')
	status = models.IntegerField(null=True, blank=True, choices=FlagStatus.choices)
	date = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ['-date']
		indexes = [
			models.Index(fields=['event_type', 'status']),
			models.Index(fields=['work', 'event_type']),
		]
		constraints = [
			# At most one pending flag/appeal per work.
			models.UniqueConstraint(
				fields=['work'],
				condition=Q(
					event_type__in=[
						ModerationEventType.FLAG,
						ModerationEventType.APPEAL,
					],
					status=FlagStatus.PENDING,
				),
				name='unique_pending_moderation_per_work',
				violation_error_message='This work already has a pending flag or appeal',
			),
			# At most one disapproval per work per user.
			models.UniqueConstraint(
				fields=['work', 'by'],
				condition=Q(event_type=ModerationEventType.DISAPPROVAL),
				name='unique_disapproval_per_work_per_user',
			),
		]
