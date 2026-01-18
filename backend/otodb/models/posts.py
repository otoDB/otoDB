from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_comments_xtd.models import XtdComment

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY

from otodb.account.models import Account
from .enums import LanguageTypes, PostCategory
from .revision import Revision


class Post(models.Model):
	title = models.CharField(max_length=1000, null=False, blank=False)
	added_by = models.ForeignKey(
		Account, blank=False, null=False, on_delete=models.CASCADE
	)
	category = models.IntegerField(
		choices=PostCategory.choices, null=False, blank=False
	)

	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'

	@property
	def pages(self):
		return self.postcontent_set


class PostContent(models.Model):
	post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE)
	page = MarkdownField(
		rendered_field='page_rendered', validator=VALIDATOR_CLASSY, null=False
	)
	page_rendered = RenderedMarkdownField()
	lang = models.IntegerField(choices=LanguageTypes.choices, null=False, blank=False)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (('post', 'lang'),)


class Notification(models.Model):
	target = models.ForeignKey(
		Account,
		blank=False,
		null=False,
		on_delete=models.CASCADE,
		related_name='notifs',
	)
	dismissed = models.BooleanField(default=False)

	revision = models.ForeignKey(
		Revision,
		blank=True,
		null=True,
		on_delete=models.CASCADE,
	)
	comment = models.ForeignKey(
		XtdComment,
		blank=True,
		null=True,
		on_delete=models.CASCADE,
	)

	class Meta:
		constraints = [
			models.CheckConstraint(
				check=(
					models.Q(revision__isnull=True) ^ models.Q(comment__isnull=True)
				),
				name='notification_union',
			)
		]


class Subscription(models.Model):
	subscriber = models.ForeignKey(
		Account,
		blank=False,
		null=False,
		on_delete=models.CASCADE,
	)
	entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	entity_id = models.PositiveBigIntegerField()
	entity = GenericForeignKey('entity_type', 'entity_id')

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['subscriber', 'entity_type', 'entity_id'],
				name='unique_subscription',
			)
		]
