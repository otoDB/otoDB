from django.db import models
from django.urls import reverse

from .media_work import MediaWork
from .media_song import MediaSong

from .enums import WorkRelationTypes, SongRelationTypes


class WorkRelation(models.Model):
    A = models.ForeignKey(MediaWork)
    B = models.ForeignKey(MediaWork)
    relation = models.IntegerField(choices=WorkRelationTypes.choices)

    def __str__(self) -> str:
        return f'{self.A} - {self.B}: {self.relation}'

    class Meta:
        verbose_name = 'Work relation'
        verbose_name_plural = 'Work relations'

    def get_absolute_url(self):
        return reverse('otodb:list', kwargs={ 'list_id': self.id })

class SongRelation(models.Model):
    A = models.ForeignKey(MediaSong)
    B = models.ForeignKey(MediaSong)
    relation = models.IntegerField(choices=SongRelationTypes.choices)

    def __str__(self) -> str:
        return f'{self.A} - {self.B}: {self.relation}'

    class Meta:
        verbose_name = 'Work relation'
        verbose_name_plural = 'Work relations'

    def get_absolute_url(self):
        return reverse('otodb:list', kwargs={ 'list_id': self.id })

