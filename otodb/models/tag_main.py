from bitfield import BitField
from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords
from tagulous.models import TagModel

from .category import Category
from .enums import RoleFlags, TagCategory


class TagWork(TagModel):
    # NOTE: default=1 == 'General' -- see fixtures/category.yaml for more
    category = models.ForeignKey(Category, default=int(TagCategory.GENERAL), on_delete=models.SET_DEFAULT)  # type: ignore
    default_role_flags = BitField(RoleFlags)  # type: ignore
    # wiki_page = models.OneToOneField('wiki.article', on_delete=models.SET_NULL, null=True, blank=True)
    aliased_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='aliases')
    history = HistoricalRecords()

    @property
    def display_name(self):
        return self.name.replace('_', ' ')

    def __str__(self):
        return self.name

    def clean(self):
        if ' ' in self.name or ' ' in self.slug:
            raise ValidationError('Singular tag must not contain spaces')
        if self.default_role_flags.mask != 0:
            if self.category.id != TagCategory.CREATOR:
                raise ValidationError('Role flags can only be set for creator tags')

    class Meta:
        verbose_name = ("Tag")
        verbose_name_plural = ("Tags")
        permissions = [
            ("manage_tags", "Can manage tags"),
        ]

    class TagMeta:
        protect_all = True
        force_lowercase = True
