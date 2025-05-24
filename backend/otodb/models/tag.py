from typing import Self

from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagModel, TagModelManager

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from .enums import WorkTagCategory, SongTagCategory, LanguageTypes

def name_cleaner(s):
    return s.lower().replace('・', '')

class LowerCaseTagModelManager(TagModelManager):
    def get_or_create(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['name'] = name_cleaner(kwargs['name'])
        return super().get_or_create(*args, **kwargs)

    def get(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['name'] = name_cleaner(kwargs['name'])
        return super().get(*args, **kwargs)

class WikiPage(models.Model):
    page = MarkdownField(rendered_field='page_rendered', validator=VALIDATOR_STANDARD, null=False)
    page_rendered = RenderedMarkdownField()
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)

    history = HistoricalRecords()

class TagWork(TagModel):
    objects = LowerCaseTagModelManager()

    class TagMeta:
        protect_all = True
        case_sensitive = False
        force_lowercase = True

    def save(self, *args, **kwargs):
        if self.name:
            self.name = name_cleaner(self.name)
        super().save(*args, **kwargs)

    category = models.IntegerField(choices=WorkTagCategory.choices, default=WorkTagCategory.GENERAL)
    wiki_page = models.OneToOneField(WikiPage, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)
    history = HistoricalRecords()

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    def get_tree(self):
        tree = []
        curr = self
        while curr is not None:
            tree.append(curr)
            curr = curr.parent
        return reversed(tree)

    def get_song(self):
        if hasattr(self, 'mediasong'):
            return self.mediasong

    @staticmethod
    def alias(from_tags: list[Self], into_tag: Self):
        for tag in from_tags:
            if tag.id != into_tag.id:
                tag.aliased_to = into_tag
                tag.save()
                for work in tag.works.all():
                    work.tags.add(into_tag)
                    work.tags.remove(tag)
                for t in TagWork.objects.filter(aliased_to=tag):
                    t.aliased_to = into_tag
                    t.save()
                for t in TagWork.objects.filter(parent=tag):
                    t.parent = into_tag
                    t.save()
                if into_tag.parent is None:
                    into_tag.parent = tag.parent
                if tag.category == WorkTagCategory.SONG:
                    song = tag.mediasong
                    song.work_tag = into_tag
                    song.save()
                    
        into_tag.save()


class TagSong(TagModel):
    objects = LowerCaseTagModelManager()

    class TagMeta:
        protect_all = True
        case_sensitive = False
        force_lowercase = True

    def save(self, *args, **kwargs):
        if self.name:
            self.name = name_cleaner(self.name)
        super().save(*args, **kwargs)

    category = models.IntegerField(choices=SongTagCategory.choices, default=SongTagCategory.GENERAL)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    history = HistoricalRecords()

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    def get_tree(self):
        tree = []
        curr = self
        while curr is not None:
            tree.append(curr)
            curr = curr.parent
        return reversed(tree)

    @staticmethod
    def alias(from_tags: list[Self], into_tag: Self):
        for tag in from_tags:
            if tag.id != into_tag.id:
                tag.aliased_to = into_tag
                tag.save()
                for work in tag.works.all():
                    work.tags.add(into_tag)
                    work.tags.remove(tag)
                for t in TagSong.objects.filter(aliased_to=tag):
                    t.aliased_to = into_tag
                    t.save()
                for t in TagSong.objects.filter(parent=tag):
                    t.parent = into_tag
                    t.save()
                if into_tag.parent is None:
                    into_tag.parent = tag.parent
                    
        into_tag.save()
