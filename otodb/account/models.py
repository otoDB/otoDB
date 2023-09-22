from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from rolepermissions.roles import assign_role
from typing import TYPE_CHECKING

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
    # first_name = None
    # last_name = None
    email_activated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    if TYPE_CHECKING:
        id: int

    def save(self, *args, **kwargs):
        give_role = False
        if self._is_a_new_user():
            give_role = True
        
        super(Account, self).save(*args, **kwargs)

        if give_role:
            if self.is_staff:
                assign_role(self, 'administrator')
            else:
                assign_role(self, 'user')

    def _is_a_new_user(self):
        return not self.id
