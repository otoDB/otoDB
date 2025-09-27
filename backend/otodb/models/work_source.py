from datetime import date
from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords, HistoricForeignKey
import requests

from .enums import Platform, WorkOrigin, WorkStatus, MimeType
from .media import MediaWork

from otodb.account.models import Account
from otodb.common import video_info, process_video_info
from otodb.storage_manager import storage_manager

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(rejection__isnull=True)

class WorkSource(models.Model):
    media = HistoricForeignKey(MediaWork, on_delete=models.CASCADE, null=True, blank=True)
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
    thumbnail_url = models.URLField(null=True, blank=False)
    thumbnail_mime = models.IntegerField(
        choices=MimeType.choices,
        null=True,
        blank=True
    )
    uploader_id = models.CharField(max_length=1000, null=True, blank=False)

    added_by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.CASCADE)

    objects = models.Manager()
    active_objects = ActiveManager()
    history = HistoricalRecords()

    info_payload: 'WorkSourceInfoPayload'

    def __str__(self) -> str:
        return f'#{self.media.pk} - {self.url}' if self.media else self.title

    class Meta:
        verbose_name = ("Media Source")
        verbose_name_plural = ("Media Sources")
        ordering = ['work_status', 'work_origin', 'published_date']

    def refresh(self, use_cache=False):
        """
        Refresh work source information.

        Args:
            use_cache: If `True`, use previously cached payload instead of requesting new data.
        """
        full_info = None

        if use_cache and getattr(self, 'info_payload', None):
            info = process_video_info(self.info_payload.payload, self.url)
        else:
            info, full_info = video_info(self.url)

        if info:
            self.title = info['title']
            self.description = info['description']
            self.uploader_id = info['uploader_id']
            self.thumbnail_url = info.get('thumb', self.thumbnail_url)
            self.thumbnail_mime = info.get('thumb_mime', self.thumbnail_mime)
            self.work_width = info.get('work_width', self.work_width)
            self.work_height = info.get('work_height', self.work_height)
            self.work_duration = info.get('work_duration', self.work_duration)

            # Re-upload thumbnail to CDN for non-cached refreshes
            if not use_cache and self.thumbnail_url and self.thumbnail_mime:
                self.save_thumbnail()

            if full_info is not None:
                WorkSourceInfoPayload.objects.update_or_create(source=self, defaults={ 'payload': full_info })

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

    def save_thumbnail(self):
        if not self.thumbnail_url or not self.thumbnail_mime:
            return False
        try:
            response = requests.get(self.thumbnail_url, timeout=10)
            response.raise_for_status()
            path = storage_manager.save(response.content, self.thumbnail_path)

            if path:
                return True
            else:
                print(f"Failed to upload thumbnail for WorkSource {self.pk}")
                return False
        except Exception as e:
            print(f"Error uploading thumbnail for WorkSource {self.pk}: {e}")
            return False

    # Gets the source registered at the url if it exists, otherwise register as pending
    @staticmethod
    def from_url(url, user, is_reupload, info=None, full_info=None):
        if info is None:
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
                work_origin=WorkOrigin(is_reupload), thumbnail_url=info.get('thumb', None), thumbnail_mime=info.get('thumb_mime', None),
                work_width=info.get('work_width', None), work_height=info.get('work_height', None), work_duration=info.get('work_duration', None),
                added_by=user, uploader_id=info['uploader_id'])
            WorkSourceInfoPayload.objects.create(source=src, payload=full_info)

            if src.thumbnail_url and src.thumbnail_mime:
                src.save_thumbnail()

        return src, info

    @property
    def thumbnail_path(self) -> str:
        """
        Returns the path from where thumbnails are located.
        """
        ext = MimeType.extension(self.thumbnail_mime)
        path = f"/t/source/{str(self.pk).zfill(2)[-2:]}/{self.pk}.{ext}"
        return path

    @property
    def thumbnail(self) -> str:
        """
        Returns the URL endpoint from which a thumbnail is served.
        """
        if self.thumbnail_path and settings.OTODB_CDN_ENABLED:
            return settings.OTODB_CDN_HOST + settings.OTODB_CDN_ROOT + self.thumbnail_path
        elif (
            self.thumbnail_path
            and storage_manager.exists(self.thumbnail_path)
		):
            # Fallback to local storage
            return settings.MEDIA_URL + self.thumbnail_path.lstrip('/')
        return self.thumbnail_url # type: ignore -- Fallback to 3rd-party remote thumbnail URL

class WorkSourceRejection(models.Model):
    source = models.OneToOneField(WorkSource, null=False, on_delete=models.CASCADE, related_name='rejection')
    reason = models.CharField(max_length=1000, null=False, blank=False)
    by = models.ForeignKey(Account, blank=False, null=False, on_delete=models.RESTRICT)

class WorkSourceInfoPayload(models.Model):
    source = models.OneToOneField(WorkSource, blank=False,null=False,on_delete=models.CASCADE, related_name='info_payload')
    payload = models.JSONField(null=False, blank=False)
