import logging

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import HashIndex
from django.db import models

from otodb.models.enums import RevisionChain, Route

logger = logging.getLogger(__name__)


class Revision(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True
	)
	date = models.DateTimeField(auto_now_add=True)
	message = models.TextField(null=False, default='')


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
		indexes = [
			models.Index(
				fields=['target_type', 'target_id'], name='revisionchange_target_idx'
			),
			models.Index(
				fields=['target_column', 'target_type'],
				name='revisionchange_column_idx',
			),
			HashIndex(
				fields=['target_value'],
				name='revisionchange_value_hash_idx',
			),
		]
		constraints = [
			models.CheckConstraint(
				condition=~models.Q(deleted=True, restored=True),
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
		indexes = [
			models.Index(
				fields=['entity_type', 'entity_id'],
				name='revisionchangeentity_ent_idx',
			),
		]


class _RevisionMetaConfig:
	"""Holds revision tracking configuration for a model"""

	def __init__(
		self,
		tracked_fields: list[str] | None = None,
		entity_attrs: list[str] | None = None,
		chain: RevisionChain = RevisionChain.STRONG,
		to_active=None,
	):
		self.tracked_fields = tracked_fields or []
		self.entity_attrs = entity_attrs or []
		self.chain = chain
		self.to_active = to_active


class RevisionTrackedModel(models.Model):
	"""Marker base for models whose edits are captured by the DB revision triggers
	(see ``otodb/revision_codegen.py``). Declaring ``class RevisionMeta`` populates
	``_revision_meta`` -- read by the trigger spec/codegen and by ``history.py`` rollback.
	Capture itself lives in the database; this class carries no runtime behavior, and
	plain/bulk ORM writes are captured because the triggers fire per row.
	"""

	class Meta:
		abstract = True

	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		if hasattr(cls, 'RevisionMeta'):
			meta = getattr(cls, 'RevisionMeta')
			cls._revision_meta = _RevisionMetaConfig(
				tracked_fields=getattr(meta, 'tracked_fields', []),
				entity_attrs=getattr(meta, 'entity_attrs', []),
				chain=getattr(meta, 'chain', RevisionChain.STRONG),
				to_active=getattr(meta, 'to_active', None),
			)
		else:
			cls._revision_meta = _RevisionMetaConfig()
