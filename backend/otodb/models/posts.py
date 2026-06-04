from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import (
	Case,
	Count,
	DateTimeField,
	F,
	OuterRef,
	Prefetch,
	Q,
	Subquery,
	TextField,
	When,
)
from django.db.models.functions import Cast, Coalesce
from django.utils.timezone import now as tz_now
from django_comments_xtd.models import XtdComment

from .enums import LanguageTypes, NotificationReason, PostCategory
from .revision import Revision


class ThreadQuerySet(models.QuerySet):
	def with_activity(self):
		latest_post = ThreadPost.objects.filter(
			thread_id=OuterRef('id'),
			is_removed=False,
		).order_by('-num')

		return self.annotate(
			# Last activity = the most recent post's date (edits don't bump a thread)
			modified=Coalesce(
				Subquery(latest_post.values('created_at')[:1]),
				F('created_at'),
				output_field=DateTimeField(),
			),
			last_post_by=Subquery(latest_post.values('user__username')[:1]),
			last_post_at=Subquery(latest_post.values('created_at')[:1]),
			post_count=Coalesce(
				Subquery(
					ThreadPost.objects.filter(
						thread_id=OuterRef('id'), is_removed=False
					)
					.order_by()
					.values('thread_id')
					.annotate(c=Count('id'))
					.values('c')
				),
				0,
			),
		).order_by('-modified')


class ThreadManager(models.Manager):
	def with_activity(self):
		return self.get_queryset().with_activity()

	def get_queryset(self):
		from otodb.models.tag import OtodbTagModel

		from .revision import RevisionChange

		tag_models = [
			ct.id
			for ct in ContentType.objects.get_for_models(
				*OtodbTagModel.__subclasses__()
			).values()
		]
		user_model_class = apps.get_model(settings.AUTH_USER_MODEL)
		user_model = ContentType.objects.get_for_model(user_model_class).id
		return ThreadQuerySet(self.model, using=self._db).prefetch_related(
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
						When(
							Q(entity_type__id=user_model),
							then=Cast(
								Subquery(
									user_model_class.objects.filter(
										id=OuterRef('entity_id'),
									).values('username')[:1],
								),
								output_field=TextField(),
							),
						),
						default=Cast(F('entity_id'), output_field=TextField()),
					),
					ent=F('entity_type__model'),
				),
				to_attr='_entity_links',
			)
		)


class Thread(models.Model):
	title = models.CharField(max_length=1000, null=False, blank=False)
	added_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, blank=False, null=False, on_delete=models.CASCADE
	)
	category = models.IntegerField(
		choices=PostCategory.choices, null=False, blank=False
	)
	# Single language, set transparently from the user's locale at creation
	lang = models.IntegerField(choices=LanguageTypes.choices, null=False, blank=False)
	created_at = models.DateTimeField(default=tz_now)
	closed_at = models.DateTimeField(null=True, blank=True)
	is_removed = models.BooleanField(default=False, db_index=True)

	objects: ThreadManager = ThreadManager()

	if TYPE_CHECKING:
		from django.db.models import QuerySet

		entitylink_set: QuerySet['EntityLink']
		_entity_links: list['EntityLink']
		posts: QuerySet['ThreadPost']

	class Meta:
		verbose_name = 'Thread'
		verbose_name_plural = 'Threads'

	@property
	def entities(self) -> list[dict]:
		return [{'entity': link.ent, 'id': link.tg_id} for link in self._entity_links]


class ThreadPost(models.Model):
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts')
	# 1 = OP
	num = models.PositiveIntegerField()
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, blank=False, null=False, on_delete=models.CASCADE
	)
	body = models.TextField()
	# default=tz_now (not auto_now_add) so the data migration can set historical dates
	created_at = models.DateTimeField(default=tz_now)
	edited_at = models.DateTimeField(null=True, blank=True)
	edited_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='edited_threadposts',
	)
	is_removed = models.BooleanField(default=False, db_index=True)

	class Meta:
		ordering = ['num']
		constraints = [
			models.UniqueConstraint(
				fields=['thread', 'num'], name='threadpost_unique_num'
			),
			# The opening post (num=1) should never be soft-removed
			models.CheckConstraint(
				condition=Q(num__gt=1) | Q(is_removed=False),
				name='threadpost_op_kept',
			),
		]


class Notification(models.Model):
	target = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		blank=False,
		null=False,
		on_delete=models.CASCADE,
		related_name='notifs',
	)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)
	dismissed = models.BooleanField(default=False)
	reason = models.IntegerField(
		choices=NotificationReason.choices, default=NotificationReason.REPLY
	)

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
	# Thread activity points at a specific post (the OP for thread-level
	# notifications, the reply itself for replies).
	threadpost = models.ForeignKey(
		ThreadPost,
		blank=True,
		null=True,
		on_delete=models.CASCADE,
	)

	class Meta:
		ordering = ['dismissed', '-id']
		constraints = [
			models.CheckConstraint(
				condition=(
					models.Q(
						revision__isnull=False,
						comment__isnull=True,
						threadpost__isnull=True,
					)
					| models.Q(
						revision__isnull=True,
						comment__isnull=False,
						threadpost__isnull=True,
					)
					| models.Q(
						revision__isnull=True,
						comment__isnull=True,
						threadpost__isnull=False,
					)
				),
				name='notification_union',
			)
		]


class Subscription(models.Model):
	subscriber = models.ForeignKey(
		settings.AUTH_USER_MODEL,
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
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='edited_comments',
	)


class EntityLink(models.Model):
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
	entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	entity_id = models.PositiveBigIntegerField()
	entity = GenericForeignKey('entity_type', 'entity_id')

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['entity_type', 'entity_id', 'thread'],
				name='entitylink_unique_post',
			)
		]
