from django.db import models

from .enums import WorkOrigin, WorkStatus
from .media_work import MediaWork


class WorkSource(models.Model):
    media = models.ForeignKey(MediaWork, on_delete=models.CASCADE)
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
    work_width = models.IntegerField(null=True, blank=True)
    work_height = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f'#{self.media.pk} - {self.url}'

    class Meta:
        verbose_name = ("Media Source")
        verbose_name_plural = ("Media Sources")
