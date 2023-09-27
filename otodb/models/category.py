from typing import TYPE_CHECKING

from django.db import models


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
