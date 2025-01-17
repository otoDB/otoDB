from django.db import models
from django.urls import reverse

from .media_work import MediaWork
from .media_song import MediaSong

from .enums import WorkRelationTypes, SongRelationTypes


class WorkRelation(models.Model):
    A = models.ForeignKey(MediaWork, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_A')
    B = models.ForeignKey(MediaWork, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_B')
    relation = models.IntegerField(choices=WorkRelationTypes.choices)

    def __str__(self) -> str:
        return f'{self.A.id} -->|{WorkRelationTypes(self.relation).label}| {self.B.id}'

    class Meta:
        verbose_name = 'Work relation'
        verbose_name_plural = 'Work relations'
        constraints = [
            models.UniqueConstraint(fields=["A", "B"], name="unique_relation_between_works"),
            models.CheckConstraint(
                name="work_relation_nonreflexive",
                check=models.Q(A__ne=models.F("B")),
                violation_error_message="A must be different from B",
            ),
        ]

    def get_relations_including_works(works):
        return WorkRelation.objects.filter(A__in=works) | WorkRelation.objects.filter(B__in=works)

    def get_component_from_work(work: MediaWork):
        # TODO plenty of room for optimization here
        def get_works_from_relations(relations):
            return (MediaWork.objects.filter(relation_A__in=relations) | MediaWork.objects.filter(relation_B__in=relations)).distinct()

        component = WorkRelation.get_relations_including_works([work])
        works = get_works_from_relations(component)
        while True:
            last_size = len(works)
            component = WorkRelation.get_relations_including_works(works)
            works = get_works_from_relations(component)
            if last_size == len(works):
                return component, works

class SongRelation(models.Model):
    A = models.ForeignKey(MediaSong, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_A')
    B = models.ForeignKey(MediaSong, null=False, blank=False, on_delete=models.CASCADE, related_name='relation_B')
    relation = models.IntegerField(choices=SongRelationTypes.choices)

    def __str__(self) -> str:
        return f'{self.A.id} -->|{SongRelationTypes(self.relation).label}| {self.B.id}'

    class Meta:
        verbose_name = 'Song relation'
        verbose_name_plural = 'Song relations'
        constraints = [
            models.UniqueConstraint(fields=["A", "B"], name="unique_relation_between_songs"),
            models.CheckConstraint(
                name="song_relation_nonreflexive",
                check=models.Q(A__ne=models.F("B")),
                violation_error_message="A must be different from B",
            ),
        ]

    def get_relations_including_songs(songs):
        return SongRelation.objects.filter(A__in=songs) | SongRelation.objects.filter(B__in=songs)

    def get_component_from_song(song: MediaSong):
        # TODO plenty of room for optimization here
        def get_songs_from_relations(relations):
            return (MediaSong.objects.filter(relation_A__in=relations) | MediaSong.objects.filter(relation_B__in=relations)).distinct()

        component = SongRelation.get_relations_including_songs([song])
        songs = get_songs_from_relations(component)
        while True:
            last_size = len(songs)
            component = SongRelation.get_relations_including_songs(songs)
            songs = get_songs_from_relations(component)
            if last_size == len(songs):
                return component, songs
