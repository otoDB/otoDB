from django.db import models

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY

from otodb.account.models import Account
from .enums import LanguageTypes, PostCategory


class Post(models.Model):
    title = models.CharField(max_length=1000, null=False, blank=False)
    added_by = models.ForeignKey(
        Account, blank=False, null=False, on_delete=models.CASCADE
    )
    category = models.IntegerField(
        choices=PostCategory.choices, null=False, blank=False
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    @property
    def pages(self):
        return self.postcontent_set


class PostContent(models.Model):
    post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE)
    page = MarkdownField(
        rendered_field="page_rendered", validator=VALIDATOR_CLASSY, null=False
    )
    page_rendered = RenderedMarkdownField()
    lang = models.IntegerField(choices=LanguageTypes.choices, null=False, blank=False)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("post", "lang"),)
