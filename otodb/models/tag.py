from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagModel

from .enums import WorkTagCategory, SongTagCategory


class TagWork(TagModel):
    category = models.IntegerField(choices=WorkTagCategory.choices, default=WorkTagCategory.GENERAL)
    # TODO wiki_page = models.OneToOneField('wiki.article', on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    history = HistoricalRecords()

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("Work Tag")
        verbose_name_plural = ("Work Tags")
        permissions = [
            ("manage_tags", "Can manage tags"),
        ]
        constraints = [
            models.CheckConstraint(
                name="work_tag_song_not_null",
                check=models.Q(category__ne=WorkTagCategory.SONG) | models.Q(category=WorkTagCategory.SONG, mediasong__isnull=False),
            ),
        ]

    class TagMeta:
        protect_all = True
        force_lowercase = True

    def get_absolute_url(self):
        return reverse('otodb:tag', kwargs={ 'tag_id': self.id })

    def get_tree(self):
        tree = []
        curr = self
        while curr is not None:
            tree.append(curr)
            curr = curr.parent
        return reversed(tree)

class TagSong(TagModel):
    category = models.IntegerField(choices=SongTagCategory.choices, default=SongTagCategory.GENERAL)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    history = HistoricalRecords()

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")
        permissions = [
            ("manage_tags", "Can manage tags"),
        ]

    class TagMeta:
        protect_all = True
        force_lowercase = True

    def get_absolute_url(self):
        return reverse('otodb:tag_song', kwargs={ 'tag_id': self.id })


