from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.level = Account.Levels.OWNER
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    class Levels(models.IntegerChoices):
        ANONYMOUS = 0
        RESTRICTED = 10
        MEMBER = 20
        MODERATOR = 40
        ADMIN = 50
        OWNER = 100

    level = models.IntegerField(choices=Levels.choices, default=Levels.MEMBER)
    email_activated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = AccountManager()

    if TYPE_CHECKING:
        id: int

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)

    @property
    def is_moderator(self):
        return self.level >= self.Levels.MODERATOR
