from django.db import models

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY

from otodb.account.models import Account

class Post(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    added_by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)
    post = MarkdownField(rendered_field='post_rendered', validator=VALIDATOR_CLASSY, null=False)
    post_rendered = RenderedMarkdownField()

    class Meta:
        verbose_name = ("Post")
        verbose_name_plural = ("Posts")
