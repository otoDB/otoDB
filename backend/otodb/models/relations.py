from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query import prefetch_related_objects

from .media import MediaWork, MediaSong

from .enums import WorkRelationTypes, SongRelationTypes

class BidirectionalManager(models.Manager):
    def get(self, A, B):
        try:
            return super().get(A=A, B=B)
        except ObjectDoesNotExist:
            return super().get(B=A, A=B)


class WorkRelation(models.Model):
    A = models.ForeignKey(MediaWork, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_A')
    B = models.ForeignKey(MediaWork, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_B')
    relation = models.IntegerField(choices=WorkRelationTypes.choices)

    objects = BidirectionalManager()

    def __str__(self) -> str:
        return f'{self.A.pk} -> {self.B.pk}: {WorkRelationTypes(self.relation).label}'

    class Meta:
        verbose_name = 'Work relation'
        verbose_name_plural = 'Work relations'
        constraints = [
            models.UniqueConstraint(fields=["A", "B"], name="unique_relation_between_works"),
            models.CheckConstraint(
                name="work_relation_nonreflexive",
                check=~models.Q(A=models.F("B")),
                violation_error_message="A must be different from B",
            ),
        ]

    @staticmethod
    def get_component(work_id: int):
        query = list(WorkRelation.objects.raw('''
            WITH RECURSIVE component AS (
                SELECT "otodb_workrelation"."id", "otodb_workrelation"."A_id", "otodb_workrelation"."B_id", "otodb_workrelation"."relation" FROM "otodb_workrelation" WHERE "otodb_workrelation"."A_id" = %s OR "otodb_workrelation"."B_id" = %s
                UNION
                SELECT r.id, r."A_id", r."B_id", r.relation FROM otodb_workrelation r
                JOIN component c ON c."A_id" = r."B_id" OR c."B_id" = r."A_id" OR c."A_id" = r."A_id" OR c."B_id" = r."B_id"
            )
            SELECT * FROM component;
        ''', [work_id, work_id]))
        prefetch_related_objects(query, 'A', 'B')
        return query

class SongRelation(models.Model):
    A = models.ForeignKey(MediaSong, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_A')
    B = models.ForeignKey(MediaSong, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_B')
    relation = models.IntegerField(choices=SongRelationTypes.choices)

    objects = BidirectionalManager()

    def __str__(self) -> str:
        return f'{self.A.pk} -->|{SongRelationTypes(self.relation).label}| {self.B.pk}'

    class Meta:
        verbose_name = 'Song relation'
        verbose_name_plural = 'Song relations'
        constraints = [
            models.UniqueConstraint(fields=["A", "B"], name="unique_relation_between_songs"),
            models.CheckConstraint(
                name="song_relation_nonreflexive",
                check=~models.Q(A=models.F("B")),
                violation_error_message="A must be different from B",
            ),
        ]
    @staticmethod
    def get_component(song_id: int):
        query = list(SongRelation.objects.raw('''
            WITH RECURSIVE component AS (
                SELECT "otodb_songrelation"."id", "otodb_songrelation"."A_id", "otodb_songrelation"."B_id", "otodb_songrelation"."relation" FROM "otodb_songrelation" WHERE "otodb_songrelation"."A_id" = %s OR "otodb_songrelation"."B_id" = %s
                UNION
                SELECT r.id, r."A_id", r."B_id", r.relation FROM otodb_songrelation r
                JOIN component c ON c."A_id" = r."B_id" OR c."B_id" = r."A_id" OR c."A_id" = r."A_id" OR c."B_id" = r."B_id"
            )
            SELECT * FROM component;
        ''', [song_id, song_id]))
        prefetch_related_objects(query, 'A', 'B')
        return query
