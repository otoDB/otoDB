from django.core.exceptions import ValidationError
from django.db import models

from ..models import TagWork


class WikiPage(models.Model):
    slug = models.SlugField(unique=True)
    body = models.TextField(default="")
    other_names = models.CharField(null=True, blank=True, max_length=1000)

    def clean(self):
        if ':' in self.slug:
            return

        if not TagWork.objects.filter(slug=self.slug).exists():
            raise ValidationError('Wiki page must match existing tag slug, or use namespace prefix')
