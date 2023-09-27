from typing import TYPE_CHECKING

from bitfield import BitField
from django.core.exceptions import ValidationError
from django.db import models
from taggit.models import GenericTaggedItemBase

from otodb.common import utils

from .enums import RoleFlags, TagCategory
from .tag_main import TagMain


class TaggedMedia(GenericTaggedItemBase):
    if TYPE_CHECKING:
        role_flags: BitField

    tag = models.ForeignKey(TagMain, related_name="%(app_label)s_%(class)s_items", on_delete=models.CASCADE)
    role_flags = BitField(RoleFlags)  # type: ignore

    def save(self, *args, **kwargs):
        if self.role_flags.mask == 0 and self.tag.default_role_flags.mask != 0:
            self.role_flags = self.tag.default_role_flags
        super(TaggedMedia, self).save(*args, **kwargs)
        utils.verify_and_perform_implications(self.tag)

    def clean(self):
        if self.role_flags is not None and self.role_flags.mask != 0:
            if self.tag.category.id != TagCategory.CREATOR:
                raise ValidationError('Role flags can only be set for creator tags')

    class Meta:
        verbose_name = ("Tagged Media")
        verbose_name_plural = ("Tagged Media")
