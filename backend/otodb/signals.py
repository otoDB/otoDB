from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from django_comments.signals import comment_will_be_posted
from django_comments_xtd.signals import should_request_be_authorized

from otodb.models import MediaWork, MediaSong, TagWork, TagSong
from otodb.account.models import Account


# IMPORTANT: maintain following invariants:
# - aliased tags are NOT attached to any works, table joined to alias as soon as aliasing happens
# - a tag that is aliased to another tag cannot itself be an alias target, all alias targets must have alised_to = null
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

# DRF handler for django_comments_xtd
@receiver(should_request_be_authorized)
def check_comments_logged_in(sender, comment, request, **kwargs):
    return request.user and request.user.is_authenticated   

# Place zero trust on incoming request
# for some reason django_comments_xtd allows request to specify name and email even when authenticated
@receiver(comment_will_be_posted)
def unbastardize_poster_info(sender, comment, request, **kwargs):
    if request.user.level < Account.Levels.MEMBER:
        return False # Discard
    comment['user_name'] = request.user.username
    comment['user_email'] = request.user.email
