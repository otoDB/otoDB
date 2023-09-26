from django.db import models
from django.core.exceptions import ValidationError
from ..models import TagMain


class WikiPage(models.Model):
    slug = models.SlugField(unique=True)
    body = models.TextField(default="")

    def clean(self):
        if ':' in self.slug:
            return

        if not TagMain.objects.filter(slug=self.slug).exists():
            raise ValidationError('Wiki page must match existing tag slug, or use namespace prefix')
