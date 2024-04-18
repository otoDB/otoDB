from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models

from otodb.managers import UserManager


class Priviledge(models.Model):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=127)

    class Meta:
        verbose_name = 'priviledge'
        verbose_name_plural = 'priviledges'
        ordering = ['codename']

    def __str__(self) -> str:
        return f'{self.codename} | {self.name}'


class Account(AbstractUser):
    email_activated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    if TYPE_CHECKING:
        id: int

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)

    def _is_a_new_user(self):
        return not self.id
