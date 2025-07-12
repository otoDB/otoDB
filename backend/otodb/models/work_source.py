from datetime import date
from django.db import models

from .enums import Platform, WorkOrigin, WorkStatus
from .media import MediaWork

from otodb.account.models import Account
from otodb.common import video_info, process_video_info

from furl import furl

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(rejection__isnull=True)

class WorkSource(models.Model):
    media = models.ForeignKey(MediaWork, on_delete=models.CASCADE, null=True)
    platform = models.IntegerField(choices=Platform.choices)
    source_id = models.CharField(max_length=1000)

    url = models.URLField(null=False, blank=False)
    published_date = models.DateField(auto_now=False, auto_now_add=False)
    work_origin = models.IntegerField(
        choices=WorkOrigin.choices,
        default=WorkOrigin.AUTHOR
    )
    work_status = models.IntegerField(
        choices=WorkStatus.choices,
        default=WorkStatus.AVAILABLE
    )
    work_width = models.PositiveIntegerField(null=True, blank=True)
    work_height = models.PositiveIntegerField(null=True, blank=True)
    work_duration = models.PositiveIntegerField(null=True, blank=True)

    title = models.CharField(max_length=1000, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=False)
    uploader_id = models.CharField(max_length=1000, null=False, blank=False)

    added_by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)

    info_payload = models.JSONField(null=True, blank=True)

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self) -> str:
        return f'#{self.media.pk} - {self.url}' if self.media else self.title

    class Meta:
        verbose_name = ("Media Source")
        verbose_name_plural = ("Media Sources")
        ordering = ['-published_date']

    def refresh(self, use_cache=False):
        """
        Refresh work source information.

        Args:
            use_cache: If True, use existing info_payload instead of requesting new data.
        """
        full_info = None

        if use_cache and self.info_payload:
            info = process_video_info(self.info_payload, self.url)
        else:
            info, full_info = video_info(self.url)

        if info:
            self.title = info['title']
            self.description = info['description']
            self.uploader_id = info['uploader_id']
            self.thumbnail = info.get('thumb', self.thumbnail)
            self.work_width = info.get('work_width', self.work_width)
            self.work_height = info.get('work_height', self.work_height)
            self.work_duration = info.get('work_duration', self.work_duration)

            if full_info is not None:
                self.info_payload = full_info

            if self.media:
                from .tag import TagWork
                new_tags = []
                for tag in info.get('tags', []):
                    try:
                        tag_obj, created = TagWork.objects.get_or_create(name=tag)
                        self.media.tags.add(tag_obj)
                        if created:
                            new_tags.append(tag_obj.pk)
                    except Exception:
                        tag_obj = TagWork.objects.get(name=tag)
                        self.media.tags.add(tag_obj)
                if new_tags:
                    self.media.tagworkinstance_set.filter(work_tag__in=new_tags).update(instance_imported_from_source=True)
        else:
            print(f"Failed to refresh WorkSource {self.pk} - {self.url}: No info found.")
            self.work_status = WorkStatus.DOWN

        self.save()

    # Gets the source registered at the url if it exists, otherwise register as pending
    @staticmethod
    def from_url(url, user, is_reupload, info=None):
        if info is None:
            if "list=" in url:
                f = furl(url)
                f.remove(["list"])
                url = f.url
            info, full_info = video_info(url)

        if info is None:
            print(f"Failed to get video info for URL: {url}")
            return None

        if info['site'] is None:
            return None

        try:
            src = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
        except WorkSource.DoesNotExist:
            src = WorkSource.objects.create(media=None, title=info['title'], description=info['description'],
                url=info['url'], platform=info['site'], source_id=info['id'],
                published_date=date.fromtimestamp(info['timestamp']),
                work_origin=WorkOrigin(is_reupload), thumbnail=info.get('thumb', None),
                work_width=info.get('work_width', None), work_height=info.get('work_height', None), work_duration=info.get('work_duration', None),
                added_by=user, uploader_id=info['uploader_id'],
                info_payload=full_info if full_info else None)
        return src, info

class WorkSourceRejection(models.Model):
    source = models.OneToOneField(WorkSource, null=False, on_delete=models.CASCADE, related_name='rejection')
    reason = models.CharField(max_length=1000, null=False, blank=False)
    by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.RESTRICT)
