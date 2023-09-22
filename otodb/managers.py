from django.contrib.auth.models import UserManager as AbstractUserManager
from django.db import models

class UserQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(is_deleted=True)

class UserManager(AbstractUserManager):
    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()
