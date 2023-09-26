from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver
from taggit.models import TagBase
from taggit.managers import TaggableManager
from simple_history.models import HistoricalRecords
from bitfield import BitField

from .category import Category
from .enums import RoleFlags, TagCategory


class TagMain(TagBase):
    # NOTE: default=1 == 'General' -- see fixtures/otodb/category.yaml for more
    category = models.ForeignKey(Category, default=int(TagCategory.GENERAL), on_delete=models.SET_DEFAULT) # type: ignore
    aliases = TaggableManager(
        verbose_name="Aliases",
        help_text="An optional space-separated list of tag aliases.",
        blank=True,
    )
    history = HistoricalRecords()
    default_role_flags = BitField(RoleFlags) # type: ignore
    wiki_page = models.OneToOneField('wiki.WikiPage', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    def clean(self):
        if self.default_role_flags.mask != 0:
            if self.category.id != TagCategory.CREATOR:
                raise ValidationError('Role flags can only be set for creator tags')

    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")
        permissions = [
            ("manage_tags", "Can manage tags"),
        ]

# NOTE: This is not ideal because the `contains` filter could match on
#       a substring of a tag, and thus have to check more rows.
@receiver(post_delete, sender=TagMain)
def on_post_delete_tag_main(sender, instance, using, **kwargs):
    from .media import Media
    for media in Media.objects.filter(tags_mirror__contains=instance.name):
        media.check_and_update_mirror(record_history=True)
