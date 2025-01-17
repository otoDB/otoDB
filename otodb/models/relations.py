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
        ]

    def get_absolute_url(self):
        return reverse('otodb:list', kwargs={ 'list_id': self.id })

    def get_relations_including_works(works):
        return WorkRelation.objects.filter(A__in=works) | WorkRelation.objects.filter(B__in=works)

    def get_component_from_work(work: MediaWork):
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
        return f'{self.A} - {self.B}: {self.relation}'

    class Meta:
        verbose_name = 'Song relation'
        verbose_name_plural = 'Song relations'
        constraints = [
            models.UniqueConstraint(fields=["A", "B"], name="unique_relation_between_songs"),
        ]

    def get_absolute_url(self):
        return reverse('otodb:list', kwargs={ 'list_id': self.id })

