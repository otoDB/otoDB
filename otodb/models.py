from django.db import models
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase
from typing import TYPE_CHECKING, Any

from otodb.account.models import Account
from otodb import utils

class Rating(models.IntegerChoices):
        NONE = 0, "None"
        GENERAL = 1, "General"
        SENSITIVE = 2, "Sensitive"
        QUESTIONABLE = 3, "Questionable"
        EXPLICIT = 4, "Explicit"

class Implication(models.Model):
    from_tag = models.ForeignKey("otodb.TagMain", blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="from_implications")
    to_tag = models.ForeignKey("otodb.TagMain", blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="to_implications")
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL, related_name="authored_implications")
    approver = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name="approved_implications")
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        APPROVED = 1, "Approved"
        UNAPPROVED = 2, "Unapproved"

    status = models.IntegerField(
        choices=Status.choices,
        default=Status.PENDING
    )

    def __str__(self) -> str:
        return f'{self.from_tag} -> {self.to_tag}'

class Category(models.Model):
    if TYPE_CHECKING:
        id: int

    label = models.CharField(max_length=100, blank=True)
    title_singular = models.CharField(max_length=100, blank=True)
    title_plural = models.CharField(max_length=100, blank=True)
    shortcut = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=6, blank=True)

    def __str__(self) -> str:
        return f'{self.title_singular}'

    class Meta:
        verbose_name_plural = 'Categories'

class TagMain(TagBase):
    # NOTE: default=1 == 'General' -- see fixtures/otodb/category.yaml for more
    category = models.ForeignKey(Category, default=1, on_delete=models.SET_DEFAULT) # type: ignore
    aliases = TaggableManager(
        verbose_name="Aliases",
        help_text="An optional space-separated list of tag aliases.",
        blank=True,
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")
        permissions = [
            ("manage_tags", "Can manage tags"),
        ]

class TaggedMedia(GenericTaggedItemBase):
    tag = models.ForeignKey(TagMain, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(TaggedMedia, self).save(*args, **kwargs)
        utils.verify_and_perform_implications(self.tag)

class Media(models.Model):
    if TYPE_CHECKING:
        id: int

    parent = models.IntegerField(null=True, blank=True)
    media = models.CharField(max_length=255, null=False, blank=False)
    media_width = models.IntegerField(null=True, blank=True)
    media_height = models.IntegerField(null=True, blank=True)
    tags = TaggableManager(
        through=TaggedMedia,
        related_name="media",
        help_text="A space-separated list of tags."
    )
    tags_mirror = models.CharField(
        max_length=1000,
        blank=True,
        editable=False,
    )

    history = HistoricalRecords()
    rating = models.IntegerField(
        choices=Rating.choices,
        default=Rating.NONE
    )

    def __str__(self) -> str:
        return f'#{self.id}'

    def get_parent(self):
        if self.parent:
            return Media.objects.filter(parent=self.parent).exclude(id=self.id)
        return None

    def get_children(self):
        return Media.objects.filter(parent=self.id) or None

    def check_and_update_mirror(self):
        mirror = " ".join(self.tags.names())

        if self.tags_mirror != mirror:
            self.tags_mirror = mirror

        self.save_without_historial_record()

    def save_without_historial_record(self, *args, **kwargs):
        self.skip_history_when_saving = True

        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

    def check_and_update_implications(self):
        missing_implications = Implication.objects.filter(
            from_tag__in=self.tags.all(), status=1
        ).exclude(to_tag__in=self.tags.all()).distinct()

        if missing_implications.exists():
            for impl in missing_implications:
                self.tags.add(impl.to_tag)



class Configuration(models.Model):
    code_name = models.CharField(max_length=127, blank=False)
    value = models.TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.code_name}'

    class Meta:
        permissions = [
            ('manage_configuration', 'Can change the configurations of the application'),
        ]
