from typing import TYPE_CHECKING

from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db import IntegrityError, models
from django.utils import timezone

from otodb.models.enums import OtodbIntegerEnum

class AccountManager(BaseUserManager):
	def get_by_natural_key(self, username):
		return self.get(username__iexact=username)

	def create_user(self, username, email, password=None, **extra_fields):
		if not username:
			raise ValueError('Users must have a username')
		if not email:
			raise ValueError('Users must have an email address')
		if self.filter(username__iexact=username).exists():
			raise IntegrityError('This username is already taken')
		username = User.normalize_username(username)
		user: Account = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, username, email, password=None, **extra_fields):
		if self.filter(username__iexact=username).exists():
			raise ValueError('This username is already taken')
		user: Account = self.create_user(username, email, password, **extra_fields)
		user.email_activated = True
		user.level = Account.Levels.OWNER
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	class Levels(OtodbIntegerEnum):
		ANONYMOUS = 0
		RESTRICTED = 10
		MEMBER = 20
		EDITOR = 40
		ADMIN = 50
		OWNER = 100

	if TYPE_CHECKING:
		from django.db.models import QuerySet
		from ..models.work_source import WorkSource
		from ..models.posts import Notification
		from ..models.pool import Pool
		from ..models.connection import ProfileConnection

		worksource_set: QuerySet['WorkSource']
		notifs: QuerySet['Notification']
		pool_set: QuerySet['Pool']
		profileconnection_set: QuerySet['ProfileConnection']

	username = models.CharField(
		verbose_name='username',
		max_length=127,
		unique=True,
	)
	email = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
	)
	level = models.IntegerField(choices=Levels.choices, default=Levels.MEMBER)
	email_activated = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	date_created = models.DateTimeField(default=timezone.now)

	reset_token = models.CharField(max_length=127, unique=True, null=True)

	objects = AccountManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	if TYPE_CHECKING:
		id: int

	def __str__(self):
		return self.username

	def save(self, *args, **kwargs):
		super(Account, self).save(*args, **kwargs)

	@property
	def is_editor(self):
		return self.level >= self.Levels.EDITOR

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
		return True

	def has_perms(self, perms):
		return all(self.has_perm(p) for p in perms)

	def has_module_perms(self, app_label):
		if self.is_staff:
			return True
		return False

	def get_full_name(self):
		return self.username

	def get_absolute_url(self):
		return reverse('otodb:profile', kwargs={'user_id': self.id})


class Invitation(models.Model):
	secret = models.CharField(max_length=127, unique=True)
	level = models.IntegerField(choices=Account.Levels)
	created_by = models.ForeignKey(
		Account, on_delete=models.CASCADE, related_name='created_invitations'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	used_by = models.OneToOneField(
		Account,
		on_delete=models.CASCADE,
		related_name='used_invitation',
		null=True,
		blank=True,
	)
	used_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		status = 'Used' if self.used_by is not None else 'Available'
		return f'{Account.Levels(self.level).label} - {self.secret} ({status})'
