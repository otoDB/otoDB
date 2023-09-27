from django.db import models

from .enums import MediaOrigin, MediaStatus
from .media import Media


class MediaSource(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    url = models.URLField(null=False, blank=False)
    published_date = models.DateField(auto_now=False, auto_now_add=False)
    views = models.IntegerField(null=True, blank=True)
    views_updated = models.DateTimeField(auto_now=False, auto_now_add=True)
    media_origin = models.IntegerField(
        choices=MediaOrigin.choices,
        default=MediaOrigin.AUTHOR
    )
    media_status = models.IntegerField(
        choices=MediaStatus.choices,
        default=MediaStatus.AVAILABLE
    )
    media_width = models.IntegerField(null=True, blank=True)
    media_height = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f'#{self.media.pk} - {self.url}'

    class Meta:
        verbose_name = ("Media Source")
        verbose_name_plural = ("Media Sources")
