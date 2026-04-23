from typing import Annotated
from datetime import datetime, timedelta
import string
import logging
from pydantic import StringConstraints

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout

from ninja import Schema, Router, Field, ModelSchema
from ninja.security import django_auth
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

from otodb.account.models import Account, Invitation
from otodb.models.enums import (
	ErrorCode,
	LanguageTypes,
	Preferences,
)
from otodb.tasks import send_email

from .common import Error, ProfileSchema, user_is_editor, UserPreferenceSchema

logger = logging.getLogger(__name__)

auth_router = Router()


class UserLoginSchema(Schema):
	user_id: int
	username: str


class LoginRequestSchema(Schema):
	username: Annotated[str, StringConstraints(strip_whitespace=True)]
	password: str


@auth_router.get('/csrf')
@ensure_csrf_cookie
@csrf_exempt
def csrf(request: HttpRequest):
	return HttpResponse()


@auth_router.post(
	'/login',
	throttle=[AnonRateThrottle('5/m')],
	response={200: UserLoginSchema, 401: Error},
)
def login_endpoint(request: HttpRequest, body: LoginRequestSchema):
	user = authenticate(request, username=body.username, password=body.password)
	if user is not None:
		login(request, user)
		return {'user_id': user.id, 'username': user.username}
	return 401, {'code': ErrorCode.LOGIN_FAILED, 'data': {'message': 'Login failed.'}}


class UserStatusSchema(UserLoginSchema):
	level: Account.Levels
	user_id: int = Field(..., alias='id')
	username: str
	prefs: UserPreferenceSchema
	notifs_count: int


@auth_router.get('/status', response={200: UserStatusSchema, 401: Error})
def status(request: HttpRequest):
	if request.user.is_authenticated:
		u = request.user
		u.notifs_count = u.notifs.filter(dismissed=False).count()
		u.prefs = {
			Preferences(setting).name: value
			for setting, value in u.preferences.values_list('setting', 'value')
		}
		return u
	return 401, {'code': ErrorCode.NOT_LOGGED_IN, 'data': {'message': 'Not logged in.'}}


@auth_router.post('/logout', auth=django_auth)
def logout_endpoint(request: HttpRequest):
	logout(request)
	return {'message': 'Logged out'}


class RegisterRequestSchema(Schema):
	username: Annotated[str, StringConstraints(strip_whitespace=True)]
	password: str
	email: Annotated[str, StringConstraints(strip_whitespace=True)]
	invite: Annotated[str, StringConstraints(strip_whitespace=True)]


@auth_router.post(
	'/register',
	throttle=[AnonRateThrottle('3/h')],
	response={200: UserLoginSchema, 401: Error, 409: Error},
)
def register(request: HttpRequest, body: RegisterRequestSchema):
	invite_res = get_object_or_404(Invitation, secret=body.invite, used_by__isnull=True)
	assert body.password
	try:
		user = Account.objects.create_user(
			body.username, body.email, password=body.password, level=invite_res.level
		)
		invite_res.used_by = user
		invite_res.used_at = timezone.now()
		invite_res.save()

		login(request, user)
		return {'user_id': user.id, 'username': user.username}
	except IntegrityError:
		return 409, {
			'code': ErrorCode.USERNAME_TAKEN,
			'data': {'message': 'This username is already taken'},
		}
	except ValueError:
		return 400, {
			'code': ErrorCode.VALIDATION_ERROR,
			'data': {'message': 'A validation error occurred'},
		}


class ResetPasswordRequestSchema(Schema):
	password: str
	token: str | None = None


@auth_router.post('/reset_password', throttle=[AnonRateThrottle('3/h')])
def reset_password(request: HttpRequest, body: ResetPasswordRequestSchema):
	assert body.password
	user = request.user
	if user.is_authenticated:
		assert not body.token
	else:
		assert body.token
		user = get_object_or_404(Account, reset_token=body.token)
		user.reset_token = None
	user.set_password(body.password)
	user.save()


PASSWORD_RESET_EMAIL = {
	LanguageTypes.ENGLISH: [
		'[otodb.net] Reset Your Password',
		lambda name, token: (
			f"""Hello {name},


A request to reset your password has been issued. To reset your password, go here:
https://otodb.net/reset_password?token={token}

Do not share this link with anyone. If you did not try to reset your password, ignore this email.


otoDB
https://otodb.net/
"""
		),
	],
	LanguageTypes.JAPANESE: [
		'[otodb.net] パスワード再設定のご案内',
		lambda name, token: (
			f"""{name} 様


パスワード再設定のリクエストがありました。パスワードを再設定するには、以下のリンクにアクセスしてください：
https://otodb.net/reset_password?token={token}

このリンクを他人と共有しないでください。もしパスワード再設定のリクエストに心当たりがない場合は、このメールを無視してください。


otoDB
https://otodb.net/
"""
		),
	],
	LanguageTypes.SIMPLIFIED_CHINESE: [
		'[otodb.net] 重置您的密码',
		lambda name, token: (
			f"""{name}，您好：


我们收到一个重置您密码的请求。要重置密码，请访问：
https://otodb.net/reset_password?token={token}

请不要将此链接分享给任何人。如果您未申请重置密码，请忽略此邮件。


otoDB
https://otodb.net/
"""
		),
	],
	LanguageTypes.KOREAN: [
		'[otodb.net] 비밀번호 재설정 안내',
		lambda name, token: (
			f"""{name}님 안녕하세요,


비밀번호 재설정 요청이 접수되었습니다. 비밀번호를 재설정하려면 아래 링크를 방문하세요:
https://example.com/reset_password?token={token}

이 링크를 다른 사람과 공유하지 마십시오. 비밀번호 재설정을 요청하지 않으셨다면 이 이메일을 무시하시면 됩니다.


otoDB
https://otodb.net/
"""
		),
	],
}


def get_user_language(user, request):
	if user and hasattr(user, 'preferences'):
		if lang := user.preferences.filter(setting=Preferences.LANGUAGE).first():
			return lang
	if request:
		if locale := request.COOKIES.get('PARAGLIDE_LOCALE'):
			try:
				if lang := LanguageTypes.labels.index(locale):
					return lang
			except ValueError:
				pass
		if header := request.headers.get('Accept-Language'):
			for value, label in LanguageTypes.choices[1:]:
				if label in header:  # lol
					return value
	return LanguageTypes.ENGLISH


class SendResetTokenRequestSchema(Schema):
	email: str


@auth_router.put('/reset_password', throttle=[AnonRateThrottle('3/h')])
def send_reset_password_token(request: HttpRequest, body: SendResetTokenRequestSchema):
	try:
		user = Account.objects.get(email=body.email)
		user.reset_token = get_random_string(120, string.ascii_letters + string.digits)
		user.save()
		language = get_user_language(user, request)
		send_email.enqueue(
			subject=PASSWORD_RESET_EMAIL[language][0],
			body=PASSWORD_RESET_EMAIL[language][1](user.username, user.reset_token),
			from_email='noreply@otodb.net',
			to=[user.email],
		)
	except Account.DoesNotExist:
		pass


class InvitationSchema(ModelSchema):
	used_by: ProfileSchema | None
	used_at: datetime | None
	created_at: datetime
	level: Account.Levels

	class Meta:
		model = Invitation
		fields = ['secret']


@auth_router.get(
	'/invites',
	auth=django_auth,
	response=tuple[list[InvitationSchema], ProfileSchema | None],
)
def user_invites(request: HttpRequest):
	return 200, (
		Invitation.objects.filter(created_by=request.user).order_by('-created_at'),
		getattr(
			Invitation.objects.filter(
				created_by=request.user, used_by__level__lte=Account.Levels.RESTRICTED
			).first(),
			'used_by',
			None,
		),
	)


@auth_router.post(
	'/invite',
	auth=django_auth,
	throttle=[AuthRateThrottle('5/d')],
)
@user_is_editor
def new_invite(request: HttpRequest):
	assert (
		request.user.level >= Account.Levels.ADMIN
		or not Invitation.objects.filter(
			created_by=request.user, created_at__gte=datetime.now() - timedelta(days=7)
		).exists()
	)
	assert not Invitation.objects.filter(
		created_by=request.user, used_by__level__lte=Account.Levels.RESTRICTED
	).exists()
	Invitation.objects.create(
		created_by=request.user,
		level=Account.Levels.EDITOR,
		secret=get_random_string(16, string.ascii_letters + string.digits),
	)
