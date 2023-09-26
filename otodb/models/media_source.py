from django.db import models
from .media import Media


class MediaOrigin(models.IntegerChoices):
    AUTHOR   = 0, "Author"
    PRIMARY  = 1, "Primary"
    REUPLOAD = 2, "Reupload"


class MediaSource(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    url = models.URLField()
    media_origin = models.IntegerField(
        choices=MediaOrigin.choices,
        default=MediaOrigin.AUTHOR
    )
