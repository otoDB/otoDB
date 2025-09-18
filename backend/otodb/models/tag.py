from typing import TYPE_CHECKING
from itertools import chain

from django.db import models
from django.db.models import Value, Q
from simple_history.models import HistoricalRecords, HistoricForeignKey
from tagulous.models import BaseTagModel, TagModelManager

from django_cte import CTE, with_cte

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY

from .enums import WorkTagCategory, SongTagCategory, LanguageTypes, MediaType

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

def transfer_data(from_tag, to_tag):
    # carry over parenthood, category, wikipages, connections
    for tp in TagWorkParenthood.objects.filter(parent=from_tag):
        if TagWorkParenthood.objects.filter(tag=tp.tag, parent=to_tag).exists():
            tp.delete()
        elif not to_tag.get_paths().filter(id=tp.tag.id).exists():
            tp.parent = to_tag
            tp.save()
    for tp in TagWorkParenthood.objects.filter(tag=from_tag):
        if TagWorkParenthood.objects.filter(parent=tp.parent, tag=to_tag).exists():
            tp.delete()
        elif not to_tag.get_descendants().filter(id=tp.tag.id).exists():
            tp.tag = to_tag
            tp.save()
    if from_tag.category != WorkTagCategory.GENERAL and to_tag.category == WorkTagCategory.GENERAL:
        to_tag.category = from_tag.category
        if from_tag.category == WorkTagCategory.MEDIA:
            to_tag.media_type = from_tag.media_type
            from_tag.media_type = None
        if from_tag.category == WorkTagCategory.SONG:
            s = from_tag.mediasong
            s.work_tag = to_tag
            s.save()
        from_tag.category = WorkTagCategory.GENERAL
        from_tag.save()
    for p in from_tag.wikipage_set.all():
        try:
            page = WikiPage.objects.get(tag=to_tag, lang=p.lang)
            page.page += '\n\n'
            page.page += p.page
            page.save()
        except WikiPage.DoesNotExist:
            WikiPage.objects.create(tag=to_tag, lang=p.lang, page=p.page)
        p.delete()
    for c in chain(from_tag.tagworkconnection_set.all(), from_tag.tagworkmediaconnection_set.all(), from_tag.tagworkcreatorconnection_set.all()):
        if type(c).objects.filter(tag=to_tag,site=c.site,content_id=c.content_id).exists():
            c.delete()
        else:
            c.tag = to_tag
            c.save()
    to_tag.save()

def _alias(from_tags, into_tag):
    is_work = isinstance(into_tag, TagWork)
    model = TagWork if is_work else TagSong
    for tag in from_tags:
        if tag.aliased_to:
            tag = tag.aliased_to
        if tag.id != into_tag.id:
            tag.aliased_to = into_tag
            tag.save()
            for work in (tag.works if is_work else tag.songs).all():
                work.tags.add(into_tag)
                work.tags.remove(tag)
            for t in model.objects.filter(aliased_to=tag):
                t.aliased_to = into_tag
                t.save()
            if is_work:
                transfer_data(tag, into_tag)
            else:
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
                models.When(category=1, then=Value(0)),     # EVENT
                models.When(category=4, then=Value(10)),    # CREATOR
                models.When(category=6, then=Value(11)),    # MEDIA
                models.When(category=3, then=Value(20)),    # SOURCE
                models.When(category=2, then=Value(30)),    # SONG
                models.When(category=0, then=Value(40)),    # GENERAL
                models.When(category=5, then=Value(1000)),  # META (always last)
                default=Value(999),
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
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    history = HistoricalRecords()
    media_type = models.IntegerField(
            null=True,
            blank=True,
            help_text="Media type bitmask"
        )

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    def get_song(self):
        if self.mediasong is not None:
            return self.mediasong

    def set_media_type(self, types: list[MediaType | int]):
        if self.category != WorkTagCategory.MEDIA:
            self.media_type = None
            return

        type_value = 0
        for t in types:
            if isinstance(t, MediaType):
                type_value |= t.value
            else:
                type_value |= t
        self.media_type = type_value if type_value > 0 else None

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

    @property
    def children(self):
        return TagWork.objects.filter(childhood__parent=self, aliased_to__isnull=True)

    def get_descendants(self):
        cte = CTE.recursive(lambda cte: TagWork.objects.order_by().filter(id=self.id).values('id').union(
            cte.join(TagWork.objects.order_by(), childhood__parent_id=cte.col.id, aliased_to__isnull=True, deprecated=False).values('id'),
            all=True
        ))
        return with_cte(cte, select=cte.join(TagWork, id=cte.col.id)).exclude(id=self.id).distinct().order_by()
    
    def get_paths(self):
        cte = CTE.recursive(lambda cte: TagWork.objects.order_by().filter(id=self.id).values(
            'id', 'slug',
            fr=Value('', output_field=models.TextField()),
        ).union(
            cte.join(TagWork.objects.order_by(), parenthood__tag_id=cte.col.id, aliased_to__isnull=True, deprecated=False).values(
                'id', 'slug',
                fr=models.functions.Cast(cte.col.slug, models.TextField()),
            ),
            all=True
        ))
        return with_cte(cte, select=cte.join(TagWork, id=cte.col.id).annotate(fr=cte.col.fr)).order_by()

    @property
    def primary_path(self):
        cte = CTE.recursive(lambda cte: TagWork.objects.order_by().filter(id=self.id).values(
            'id', depth=Value(0, output_field=models.IntegerField()),
        ).union(
            cte.join(TagWork.objects.order_by(), parenthood__tag_id=cte.col.id, parenthood__primary=True, aliased_to__isnull=True, deprecated=False).values(
                'id', depth=cte.col.depth + Value(1, output_field=models.IntegerField()),
            ),
            all=True
        ))
        return with_cte(cte, select=cte.join(TagWork, id=cte.col.id).annotate(depth=cte.col.depth)).order_by('-depth').exclude(id=self.id)

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
        cte = CTE.recursive(lambda cte: TagSong.objects.order_by().filter(id=self.id).values('id','parent_id', depth=Value(0, output_field=models.IntegerField())).union(
            cte.join(TagSong.objects.order_by(), id=cte.col.parent_id).values('id','parent_id',depth=cte.col.depth + Value(1, output_field=models.IntegerField())),
            all=True
        ))
        return with_cte(cte, select=cte.join(TagSong, id=cte.col.id).annotate(depth=cte.col.depth)).order_by('-depth')

    @staticmethod
    def alias(from_tags: list['TagSong'], into_tag: 'TagSong'):
        _alias(from_tags, into_tag)

class TagSongLangPreference(models.Model):
    lang = models.IntegerField(choices=LanguageTypes.choices, default=LanguageTypes.NOT_APPLICABLE, null=False, blank=False)
    tag = models.ForeignKey(TagSong, null=False, blank=False, on_delete=models.CASCADE)

class TagWorkParenthood(models.Model):
    tag = models.ForeignKey(TagWork, null=False, blank=False, on_delete=models.CASCADE, related_name='childhood')
    parent = models.ForeignKey(TagWork, null=False, blank=False, on_delete=models.CASCADE, related_name='parenthood')
    primary = models.BooleanField(default=False)
    history = HistoricalRecords()
    class Meta:
        unique_together = (("tag", "parent"),)
        constraints = [
            models.CheckConstraint(
                name="tagwork_parenthood_nonreflexive",
                condition=~Q(tag=models.F("parent")),
                violation_error_message="tag cannot be own parent",
            ),
            models.UniqueConstraint(
                fields=['tag'],
                condition=Q(primary=True),
                name='tagwork_parenthood_at_most_one_primary'
            )
        ]
