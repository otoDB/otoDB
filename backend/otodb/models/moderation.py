from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from .enums import FlagStatus, ModerationAction, Status


class WorkFlag(models.Model):
	if TYPE_CHECKING:
		work_id: int

	work = models.ForeignKey(
		'MediaWork', on_delete=models.CASCADE, related_name='flags'
	)
	by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
	reason = models.CharField(max_length=1000, null=False, blank=False)
	status = models.IntegerField(choices=FlagStatus.choices, default=FlagStatus.PENDING)
	date = models.DateTimeField(auto_now_add=True)

	def clean(self):
		if self.status == FlagStatus.PENDING:
			from django.core.exceptions import ValidationError

			if self.work.status != Status.APPROVED:
				raise ValidationError('Cannot flag a non-approved work')
			if self.work.appeals.filter(status=FlagStatus.PENDING).exists():
				raise ValidationError('Cannot flag a work with a pending appeal')

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['work'],
				condition=models.Q(status=FlagStatus.PENDING),
				name='unique_pending_flag_per_work',
				violation_error_message='A pending flag already exists for this work',
			),
		]


class WorkAppeal(models.Model):
	if TYPE_CHECKING:
		work_id: int

	work = models.ForeignKey(
		'MediaWork', on_delete=models.CASCADE, related_name='appeals'
	)
	by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
	reason = models.CharField(max_length=1000, null=False, blank=False)
	status = models.IntegerField(choices=FlagStatus.choices, default=FlagStatus.PENDING)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['work'],
				condition=models.Q(status=FlagStatus.PENDING),
				name='unique_pending_appeal_per_work',
				violation_error_message='A pending appeal already exists for this work',
			),
		]


class WorkDisapproval(models.Model):
	work = models.ForeignKey(
		'MediaWork', on_delete=models.CASCADE, related_name='disapprovals'
	)
	reason = models.CharField(max_length=1000, null=False, blank=False)
	by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		blank=False,
		null=False,
		on_delete=models.RESTRICT,
	)
	date = models.DateTimeField(auto_now_add=True, null=False)

	class Meta:
		unique_together = (('work', 'by'),)


class WorkApproval(models.Model):
	work = models.ForeignKey(
		'MediaWork', on_delete=models.CASCADE, related_name='approvals'
	)
	by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
	date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date']


class ModAction(models.Model):
	work = models.ForeignKey(
		'MediaWork', null=True, blank=True, on_delete=models.CASCADE
	)
	source = models.ForeignKey(
		'WorkSource', null=True, blank=True, on_delete=models.SET_NULL
	)
	category = models.IntegerField(choices=ModerationAction.choices)
	by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
	description = models.CharField(max_length=1000, blank=True, default='')
	date = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ['-date']


class ModerationEvent(models.Model):
	"""Read-only model backed by the moderation_events database VIEW."""

	event_type = models.CharField(max_length=20)
	# Not truly unique across event types, but needed to suppress Django's auto-id
	event_id = models.IntegerField(primary_key=True)
	work_id = models.IntegerField(null=True)
	source_id = models.IntegerField(null=True)
	by_id = models.IntegerField()
	by_username = models.CharField(max_length=150)
	reason = models.CharField(max_length=1000)
	status = models.IntegerField(null=True)
	event_at = models.DateTimeField()

	class Meta:
		managed = False
		db_table = 'moderation_events'

	def readonly(self):
		return True
