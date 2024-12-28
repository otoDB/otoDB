from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver

from otodb.models import MediaWork, TagWork


# IMPORTANT: maintain following invariants:
# - aliased tags are NOT attached to any works, table joined to alias as soon as aliasing happens
# - a tag that is aliased to another tag cannot itself be an alias target, all alias targets must have alised_to = null
@receiver(m2m_changed, sender=MediaWork.tags.through)
def on_add_remove_tag_main(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for tag in TagWork.objects.filter(id__in=pk_set):
            if tag.aliased_to:
                instance.tags.remove(tag)
                instance.tags.add(tag.aliased_to)

# NOTE: This is not ideal because the `contains` filter could match on
#       a substring of a tag, and thus have to check more rows.
@receiver(post_delete, sender=TagWork)
def on_post_delete_tag_main(sender, instance: TagWork, using, **kwargs):
    for media in MediaWork.objects.filter(tags_mirror__contains=instance.name):
        media.check_and_update_mirror(record_history=True)
