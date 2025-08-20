from typing import TYPE_CHECKING

from django.db import models
from simple_history.models import HistoricalRecords, HistoricForeignKey
from tagulous.models import BaseTagModel, TagModelManager

from django_cte import CTE, with_cte

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY

from .enums import WorkTagCategory, SongTagCategory, LanguageTypes

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from .connection import TagWorkConnection, TagWorkMediaConnection, TagWorkCreatorConnection
    from .media import MediaSong

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

class OtodbTagModel(BaseTagModel):
    """
    Abstract base class for tag models
    """

    name = models.CharField(unique=True, max_length=255)
    slug = models.SlugField(unique=True, max_length=50, allow_unicode=True)
    count = models.IntegerField(
        default=0, help_text="Internal counter of how many times this tag is in use"
    )
    protected = models.BooleanField(
        default=False, help_text="Will not be deleted when the count reaches 0"
    )

    class Meta:
        abstract = True
        ordering = ("name",)

def _get_tree(node):
    model = type(node)
    cte = CTE.recursive(lambda cte: model.objects.order_by().filter(id=node.id).values('id','parent_id', depth=models.Value(0, output_field=models.IntegerField())).union(
        cte.join(model.objects.order_by(), id=cte.col.parent_id).values('id','parent_id',depth=cte.col.depth + models.Value(1, output_field=models.IntegerField())),
        all=True
    ))
    return with_cte(cte, select=cte.join(model, id=cte.col.id).annotate(depth=cte.col.depth)).order_by('-depth')

def _alias(from_tags, into_tag):
    is_work = isinstance(into_tag, TagWork)
    model = TagWork if is_work else TagSong
    for tag in from_tags:
        if tag.aliased_to:
            tag = tag.aliased_to
        if tag.id != into_tag.id:
            tag.aliased_to = into_tag
            tag.parent = None
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

class TagWork(OtodbTagModel):
    objects = LowerCaseTagModelManager()

    if TYPE_CHECKING:
        tagworkconnection_set: QuerySet['TagWorkConnection']
        tagworkmediaconnection_set: QuerySet['TagWorkMediaConnection']
        tagworkcreatorconnection_set: QuerySet['TagWorkCreatorConnection']
        tagworklangpreference_set: QuerySet['TagWorkLangPreference']
        aliases: QuerySet['TagWork']
        mediasong: 'MediaSong | None'

    class TagMeta:
        protect_all = True
        case_sensitive = False
        force_lowercase = True

    class Meta:
        ordering = [
            models.Case(
                models.When(category=1, then=models.Value(0)),     # EVENT
                models.When(category=4, then=models.Value(10)),    # CREATOR
                models.When(category=6, then=models.Value(11)),    # MEDIA
                models.When(category=3, then=models.Value(20)),    # SOURCE
                models.When(category=2, then=models.Value(30)),    # SONG
                models.When(category=0, then=models.Value(40)),    # GENERAL
                models.When(category=5, then=models.Value(1000)),  # META (always last)
                default=models.Value(999),
                output_field=models.IntegerField()
            ),
            'name'
        ]

    def save(self, *args, **kwargs):
        if self.name:
            self.name = name_cleaner(self.name)
        super().save(*args, **kwargs)

    deprecated = models.BooleanField(default=False, null=False)
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
        if self.mediasong is not None:
            return self.mediasong

    @staticmethod
    def alias(from_tags: list['TagWork'], into_tag: 'TagWork'):
        _alias(from_tags, into_tag)

    @property
    def lang_prefs(self):
        if self.aliased_to:
            return self.aliased_to.lang_prefs
        q = self.tagworklangpreference_set.all()
        for alias in self.aliases.all():
            q |= alias.tagworklangpreference_set.all()
        return q.distinct()

    @property
    def unaliasable(self):
        return any([
            self.wikipage_set.exists() and any([p.page.strip() != '' for p in self.wikipage_set]),
            self.tagworkconnection_set.exists(),
            self.category != WorkTagCategory.GENERAL
        ])

    @property
    def can_be_deleted(self):
        # Maximal friction to avoid accidentally deleting any user-contributed data
        return not any([self.unaliasable, self.works.exists(), self.aliased_to, self.aliases.exists()])
        
    def get_descendents(self):
        cte = CTE.recursive(lambda cte: TagWork.objects.order_by().filter(id=self.id).values('id', 'parent').union(
            cte.join(TagWork.objects.order_by(), parent=cte.col.id, aliased_to__isnull=True).values('id', 'parent'),
            all=True
        ))
        return with_cte(cte, select=cte.join(TagWork, id=cte.col.id)).exclude(id=self.id).distinct()

class TagWorkLangPreference(models.Model):
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)
    tag = HistoricForeignKey(TagWork, null=False, blank=False, on_delete=models.CASCADE)
    history = HistoricalRecords()
    class Meta:
        unique_together = (("tag", "lang"),)

class WikiPage(models.Model):
    tag = HistoricForeignKey(TagWork, on_delete=models.CASCADE, null=False, blank=False)
    page = MarkdownField(rendered_field='page_rendered', validator=VALIDATOR_CLASSY, null=False) # type: ignore
    page_rendered = RenderedMarkdownField()
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)

    history = HistoricalRecords()
    class Meta:
        unique_together = (("tag", "lang"),)

class TagSong(OtodbTagModel):
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
    def alias(from_tags: list['TagSong'], into_tag: 'TagSong'):
        _alias(from_tags, into_tag)

class TagSongLangPreference(models.Model):
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)
    tag = models.ForeignKey(TagSong, null=False, blank=False, on_delete=models.CASCADE)
