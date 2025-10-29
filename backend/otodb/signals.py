from django.db.models import Q
from django.db.models.signals import m2m_changed, pre_delete
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.contrib.sessions.models import Session

from otodb.models import MediaWork, MediaSong, TagWork, TagSong, UserRequest


# IMPORTANT: maintain following invariants:
# - aliased tags are NOT attached to any works, table joined to alias as soon as aliasing happens
# - a tag that is aliased to another tag cannot itself be an alias target, all alias targets must have aliased_to = null
@receiver(m2m_changed, sender=MediaWork.tags.through)
def on_add_remove_tag_work(sender, instance, action, pk_set, **kwargs):
	if action == 'post_add':
		for tag in TagWork.objects.filter(id__in=pk_set):
			if tag.aliased_to:
				instance.tags.remove(tag)
				instance.tags.add(tag.aliased_to)


@receiver(m2m_changed, sender=MediaSong.tags.through)
def on_add_remove_tag_song(sender, instance, action, pk_set, **kwargs):
	if action == 'post_add':
		for tag in TagSong.objects.filter(id__in=pk_set):
			if tag.aliased_to:
				instance.tags.remove(tag)
				instance.tags.add(tag.aliased_to)


@receiver(pre_delete)
def post_group_deleted(sender, instance, using, **kwargs):
	# Query tags with the instance of PostGroup and delete them
	if isinstance(instance, UserRequest) or isinstance(instance, Session):
		return

	UserRequest.objects.filter(
		(Q(A_type=ContentType.objects.get_for_model(instance)) & Q(A_id=instance.pk))
		| (Q(B_type=ContentType.objects.get_for_model(instance)) & Q(B_id=instance.pk))
	).delete()
