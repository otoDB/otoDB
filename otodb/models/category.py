from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import models

from otodb.common.regex import RE_HEX_COLOR


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

    def clean(self):
        if ' ' in self.shortcut:
            raise ValidationError('Category shortcut must not contain spaces')
        if self.shortcut != self.shortcut.lower():
            raise ValidationError('Category shortcut must be lowercase')
        if not RE_HEX_COLOR.match(self.color):
            raise ValidationError('Color must be a valid hexidecimal color code (3 or 6 chars)')

    class Meta:
        verbose_name_plural = 'Categories'
