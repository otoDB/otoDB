from typing import Self

from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagModel, TagModelManager

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from .enums import WorkTagCategory, SongTagCategory, LanguageTypes

def name_cleaner(s):
    return s.lower()

class LowerCaseTagModelManager(TagModelManager):
    def get_or_create(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['name'] = name_cleaner(kwargs['name'])
        return super().get_or_create(*args, **kwargs)

    def get(self, *args, **kwargs):
        if 'name' in kwargs:
            kwargs['name'] = name_cleaner(kwargs['name'])
        return super().get(*args, **kwargs)

def _get_tree(node):
    tree = []
    curr = node
    while curr is not None:
        tree.append(curr)
        curr = curr.parent
    return reversed(tree)

def _alias(from_tags, into_tag):
    is_work = isinstance(into_tag, TagWork)
    model = TagWork if is_work else TagSong
    for tag in from_tags:
        if tag.id != into_tag.id:
            tag.aliased_to = into_tag
            tag.save()
            for work in (tag.works if is_work else tag.songs).all():
                work.tags.add(into_tag)
                work.tags.remove(tag)
            for t in model.objects.filter(aliased_to=tag):
                t.aliased_to = into_tag
                t.save()
            for t in model.objects.filter(parent=tag):
                t.parent = into_tag
                t.save()
            if into_tag.parent is None:
                into_tag.parent = tag.parent

    into_tag.save()

class TagWork(TagModel):
    objects = LowerCaseTagModelManager()

    class TagMeta:
        protect_all = True
        case_sensitive = False
        force_lowercase = True

    class Meta:
        ordering = [
            models.Case(
                models.When(category=1, then=models.Value(0)),  # EVENT
                models.When(category=4, then=models.Value(1)),  # CREATOR
                models.When(category=3, then=models.Value(2)),  # SOURCE
                models.When(category=2, then=models.Value(3)),  # SONG
                models.When(category=0, then=models.Value(4)),  # GENERAL
                models.When(category=5, then=models.Value(5)),  # META
                default=models.Value(99),
                output_field=models.IntegerField()
            ),
            'name'
        ]

    def save(self, *args, **kwargs):
        if self.name:
            self.name = name_cleaner(self.name)
        super().save(*args, **kwargs)

    category = models.IntegerField(choices=WorkTagCategory.choices, default=WorkTagCategory.GENERAL)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    history = HistoricalRecords()

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    def get_tree(self):
        return _get_tree(self)

    def get_song(self):
        if hasattr(self, 'mediasong'):
            return self.mediasong

    @staticmethod
    def alias(from_tags: list[Self], into_tag: Self):
        _alias(from_tags, into_tag)

    @property
    def lang_prefs(self):
        if self.aliased_to:
            return self.aliased_to.lang_prefs
        q = self.tagworklangpreference_set.all()
        for alias in self.aliases.all():
            q |= alias.tagworklangpreference_set.all()
        return q.distinct()

class TagWorkLangPreference(models.Model):
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)
    tag = models.ForeignKey(TagWork, null=False, blank=False, on_delete=models.CASCADE)
    class Meta:
        unique_together = (("tag", "lang"),)

class WikiPage(models.Model):
    tag = models.ForeignKey(TagWork, on_delete=models.CASCADE, null=False, blank=False)
    page = MarkdownField(rendered_field='page_rendered', validator=VALIDATOR_STANDARD, null=False)
    page_rendered = RenderedMarkdownField()
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)

    history = HistoricalRecords()
    class Meta:
        unique_together = (("tag", "lang"),)

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
        return _get_tree(self)

    @staticmethod
    def alias(from_tags: list[Self], into_tag: Self):
        _alias(from_tags, into_tag)

class TagSongLangPreference(models.Model):
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)
    tag = models.ForeignKey(TagSong, null=False, blank=False, on_delete=models.CASCADE)
