from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

from django_cte import CTE, with_cte

from .media import MediaWork, MediaSong

from .enums import WorkRelationTypes, SongRelationTypes
from .revision import RevisionTrackedModel, RevisionTrackedManager


def _get_component(model, obj_id: int):
	cte = CTE.recursive(
		lambda cte: model.objects.filter(Q(A_id=obj_id) | Q(B_id=obj_id)).union(
			cte.join(
				model,
				Q(A_id=cte.col.B_id)
				| Q(B_id=cte.col.A_id)
				| Q(A_id=cte.col.A_id)
				| Q(B_id=cte.col.B_id),
			),
		)
	)
	# Note that we cannot use UNION ALL here because A-B will fetch each other forever.
	relations = with_cte(cte, select=cte.join(model, id=cte.col.id)).select_related(
		'A', 'B'
	)
	return relations


class BidirectionalManager(RevisionTrackedManager):
	def get(self, A, B):
		try:
			return super().get(A=A, B=B)
		except ObjectDoesNotExist:
			return super().get(B=A, A=B)


class WorkRelation(RevisionTrackedModel):
	A = models.ForeignKey(
		MediaWork,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='relation_A',
	)
	B = models.ForeignKey(
		MediaWork,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='relation_B',
	)
	relation = models.IntegerField(choices=WorkRelationTypes.choices)

	revision_tracked_fields = ['A', 'B', 'relation']

	objects = BidirectionalManager()

	def __str__(self) -> str:
		return f'{self.A.pk} -> {self.B.pk}: {WorkRelationTypes(self.relation).label}'

	class Meta:
		verbose_name = 'Work relation'
		verbose_name_plural = 'Work relations'
		constraints = [
			models.UniqueConstraint(
				fields=['A', 'B'], name='unique_relation_between_works'
			),
			models.CheckConstraint(
				name='work_relation_nonreflexive',
				check=~models.Q(A=models.F('B')),
				violation_error_message='A must be different from B',
			),
		]

	@staticmethod
	def get_component(work_id: int):
		return _get_component(WorkRelation, work_id)


class SongRelation(RevisionTrackedModel):
	A = models.ForeignKey(
		MediaSong,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='relation_A',
	)
	B = models.ForeignKey(
		MediaSong,
		null=False,
		blank=False,
		on_delete=models.CASCADE,
		related_name='relation_B',
	)
	relation = models.IntegerField(choices=SongRelationTypes.choices)
	revision_tracked_fields = ['A', 'B', 'relation']

	objects = BidirectionalManager()

	def __str__(self) -> str:
		return f'{self.A.pk} -->|{SongRelationTypes(self.relation).label}| {self.B.pk}'

	class Meta:
		verbose_name = 'Song relation'
		verbose_name_plural = 'Song relations'
		constraints = [
			models.UniqueConstraint(
				fields=['A', 'B'], name='unique_relation_between_songs'
			),
			models.CheckConstraint(
				name='song_relation_nonreflexive',
				check=~models.Q(A=models.F('B')),
				violation_error_message='A must be different from B',
			),
		]

	@staticmethod
	def get_component(song_id: int):
		return _get_component(SongRelation, song_id)
