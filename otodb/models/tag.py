from django.urls import reverse
from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagModel, TagModelManager

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from .enums import WorkTagCategory, SongTagCategory

class LowerCaseTagModelManager(TagModelManager):
    def get_or_create(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['name'] = kwargs['name'].lower()
        return super().get_or_create(*args, **kwargs)

    def get(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['name'] = kwargs['name'].lower()
        return super().get(*args, **kwargs)

class WikiPage(models.Model):
    page = MarkdownField(rendered_field='page_rendered', validator=VALIDATOR_STANDARD, null=False)
    page_rendered = RenderedMarkdownField()

    history = HistoricalRecords()

class TagWork(TagModel):
    objects = LowerCaseTagModelManager()

    class TagMeta:
        protect_all = True
        case_sensitive = False
        force_lowercase = True

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        super().save(*args, **kwargs)

    category = models.IntegerField(choices=WorkTagCategory.choices, default=WorkTagCategory.GENERAL)
    wiki_page = models.OneToOneField(WikiPage, on_delete=models.SET_NULL, null=True, blank=True)
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
    objects = LowerCaseTagModelManager()

    class TagMeta:
        protect_all = True
        case_sensitive = False
        force_lowercase = True

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        super().save(*args, **kwargs)

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
        case_sensitive = False
        force_lowercase = True

    def get_absolute_url(self):
        return reverse('otodb:tag_song', kwargs={ 'tag_id': self.id })


