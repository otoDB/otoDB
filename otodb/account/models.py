from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db import models
from django.utils import timezone


class AccountManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")
        if not email:
            raise ValueError("Users must have an email address")
        username = User.normalize_username(username)
        user: Account = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user: Account = self.create_user(username, email, password, **extra_fields)
        user.email_activated = True
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

    username = models.CharField(
        verbose_name="username",
        max_length=127,
        unique=True,
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    level = models.IntegerField(choices=Levels.choices, default=Levels.MEMBER)
    email_activated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)

    objects = AccountManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    if TYPE_CHECKING:
        id: int

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)

    @property
    def is_moderator(self):
        return self.level >= self.Levels.MODERATOR

    @property
    def is_staff(self):
        return self.level >= self.Levels.ADMIN

    @property
    def is_superuser(self):
        return self.is_staff

    @property
    def is_owner(self):
        return self.level >= self.Levels.OWNER

    def has_perm(self, perm, obj=None):
        # TODO: Implement object-level permissions
        return True

    def has_perms(self, perms):
        return all(self.has_perm(p) for p in perms)

    def has_module_perms(self, app_label):
        if self.is_owner and app_label == "account":
            return True
        if self.is_staff and app_label != "account":
            return True
        return False

    def get_full_name(self):
        return self.username
