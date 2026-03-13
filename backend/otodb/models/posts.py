from django.db import models
from django.db.models import (
	Prefetch,
	Subquery,
	OuterRef,
	F,
	Case,
	When,
	TextField,
	Q,
)
from django.db.models.functions import Cast

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_comments_xtd.models import XtdComment

from otodb.account.models import Account
from .enums import LanguageTypes, PostCategory
from .revision import Revision

from typing import TYPE_CHECKING


class PostManager(models.Manager):
	def get_queryset(self):
		from otodb.models.tag import OtodbTagModel
		from .revision import RevisionChange

		tag_models = [
			ct.id
			for ct in ContentType.objects.get_for_models(
				*OtodbTagModel.__subclasses__()
			).values()
		]
		return (
			super()
			.get_queryset()
			.prefetch_related(
				Prefetch(
					'entitylink_set',
					queryset=EntityLink.objects.order_by('id').annotate(
						tg_id=Case(
							When(
								Q(entity_type__id__in=tag_models),
								then=Subquery(
									RevisionChange.objects.filter(
										target_type_id=OuterRef('entity_type_id'),
										target_id=OuterRef('entity_id'),
										target_column='slug',
									).values('target_value')[:1]
								),
							),
							default=Cast(F('entity_id'), output_field=TextField()),
						),
						ent=F('entity_type__model'),
					),
					to_attr='_entity_links',
				)
			)
		)


class Post(models.Model):
	title = models.CharField(max_length=1000, null=False, blank=False)
	added_by = models.ForeignKey(
		Account, blank=False, null=False, on_delete=models.CASCADE
	)
	category = models.IntegerField(
		choices=PostCategory.choices, null=False, blank=False
	)
	edited_at = models.DateTimeField(null=True, blank=True)
	edited_by = models.ForeignKey(
		Account,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='edited_posts',
	)

	objects = PostManager()

	if TYPE_CHECKING:
		from django.db.models import QuerySet

		entitylink_set: QuerySet['EntityLink']
		_entity_links: list['EntityLink']
		postcontent_set: QuerySet['PostContent']

	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'

	@property
	def pages(self):
		return self.postcontent_set

	@property
	def entities(self) -> list[dict]:
		return [{'entity': link.ent, 'id': link.tg_id} for link in self._entity_links]


class PostContent(models.Model):
	post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE)
	page = models.TextField(null=False)
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
	post = models.ForeignKey(
		Post,
		blank=True,
		null=True,
		on_delete=models.CASCADE,
	)

	class Meta:
		constraints = [
			models.CheckConstraint(
				condition=(
					models.Q(
						revision__isnull=False, comment__isnull=True, post__isnull=True
					)
					| models.Q(
						revision__isnull=True, comment__isnull=False, post__isnull=True
					)
					| models.Q(
						revision__isnull=True, comment__isnull=True, post__isnull=False
					)
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


class CommentMeta(models.Model):
	comment = models.OneToOneField(
		XtdComment, on_delete=models.CASCADE, related_name='meta'
	)
	edited_at = models.DateTimeField(null=True, blank=True)
	edited_by = models.ForeignKey(
		Account,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='edited_comments',
	)


class EntityLink(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	entity_id = models.PositiveBigIntegerField()
	entity = GenericForeignKey('entity_type', 'entity_id')

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['entity_type', 'entity_id', 'post'],
				name='entitylink_unique_post',
			)
		]
