from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models

from otodb.managers import UserManager


class Account(AbstractUser):
    class Levels(models.IntegerChoices):
        ANONYMOUS = 0
        RESTRICTED = 10
        MEMBER = 20
        OWNER = 100

    level = models.IntegerField(choices=Levels.choices, default=Levels.MEMBER)
    email_activated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    if TYPE_CHECKING:
        id: int

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)
