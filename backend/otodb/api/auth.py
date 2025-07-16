import string
import smtplib
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from ninja import Schema, Router
from ninja.security import django_auth

from otodb.account.models import Account, Invitation

from .common import Error

auth_router = Router()

class UserLoginSchema(Schema):
    user_id: int
    username: str

@auth_router.get("/csrf")
@ensure_csrf_cookie
@csrf_exempt
def csrf(request):
    return HttpResponse()

@auth_router.post("/login", response={ 200: UserLoginSchema, 401: Error })
def login_endpoint(request, username: str, password: str):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return { 'user_id': user.id, 'username': user.username }
    return 401, {'message': 'Login failed.'}

class UserStatusSchema(UserLoginSchema):
    level: int

@auth_router.get("/status", response={ 200: UserStatusSchema, 401: Error })
def status(request):
    if request.user.is_authenticated:
        return { 'user_id': request.user.id, 'username': request.user.username, 'level': request.user.level }
    return 401, {'message': 'Not logged in.'}

@auth_router.post("/logout", auth=django_auth)
def logout_endpoint(request):
    logout(request)
    return {'message': 'Logged out'}

@auth_router.post("/register", response={ 200:UserLoginSchema, 401: Error, 409: Error })
def register(request, username: str, password: str, email: str, invite: str):
    invite_res = get_object_or_404(Invitation, secret=invite, used_by__isnull=True)
    assert(password)
    try:
        user = Account.objects.create_user(username, email, password=password, level=invite_res.level)
        invite_res.used_by = user
        invite_res.used_at = timezone.now()
        invite_res.save()

        login(request, user)
        return { 'user_id': user.id, 'username': user.username }
    except IntegrityError:
        return 409, {'message': 'This username is already taken'}
    except ValueError:
        return 400, {'message': 'A validation error occured'}

@auth_router.post("/reset_password")
def reset_password(request, password: str, token: str | None = None):
    assert(password)
    user = request.user
    if user.is_authenticated:
        assert(not token)
    else:
        assert(token)
        user = get_object_or_404(Account, reset_token=token)
        user.reset_token = None
    user.set_password(password)
    user.save()

@auth_router.put("/reset_password")
def send_reset_password_token(request, email: str):
    try:
        user = Account.objects.get(email=email)
        user.reset_token = get_random_string(120, string.ascii_letters+string.digits)
        user.save()
        send_mail(
            "[otodb.net] Reset Your Password",
            f"""
Hello {user.username},


A request to reset your password has been issued. To reset your password, go here:
https://otodb.net/reset_password?token={user.reset_token}

Do not share this link with anyone. If you did not try to reset your password, ignore this email.

otodb
https://otodb.net
""",
            "noreply@otodb.net",
            [user.email],
            fail_silently=False,
        )
    except Account.DoesNotExist:
        pass
    except smtplib.SMTPException as e:
        print('Could not send mail:', e)
