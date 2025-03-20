from datetime import date
from django.db import models

from .enums import Platform, WorkOrigin, WorkStatus
from .media import MediaWork

from otodb.account.models import Account
from otodb.common import video_info

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(rejection_reason__isnull=True)

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

    title = models.CharField(max_length=1000, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=False)

    added_by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)
    rejection_reason = models.CharField(max_length=1000, null=True, blank=False)

    objects = models.Manager()
    active_objects = ActiveManager()
    
    def __str__(self) -> str:
        return f'#{self.media.id} - {self.url}' if self.media else self.title

    class Meta:
        verbose_name = ("Media Source")
        verbose_name_plural = ("Media Sources")

    def refresh(self):
        info = video_info(self.url)
        self.title = info['title']
        self.description = info['description']
        self.thumbnail = info.get('thumb', None)
        self.work_width = info['work_width']
        self.work_height = info['work_height']
        self.save()

    # Gets the source registered at the url if it exists, otherwise register as pending
    @staticmethod
    def from_url(url, user, is_reupload, info=None):
        if info is None:
            info = video_info(url)
        
        if info['site'] is None:
            return None

        try:
            src = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
        except WorkSource.DoesNotExist:
            src = WorkSource.objects.create(media=None, title=info['title'], description=info['description'],
                url=info['url'], platform=info['site'], source_id=info['id'],
                published_date=date.fromtimestamp(info['timestamp']),
                work_origin=WorkOrigin(is_reupload), thumbnail=info.get('thumb', None),
                work_width=info.get('work_width', None), work_height=info.get('work_height', None),
                added_by=user)
        return src, info
