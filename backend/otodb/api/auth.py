from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from ninja import Schema, Router
from ninja.security import django_auth

from otodb.account.models import Account

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

@auth_router.post("/register", response={ 200:UserLoginSchema, 401: Error })
def register(request, username: str, password: str, email: str):
    # user = Account.objects.create_user(username, email, password=password)
    # login(request, user)
    # return { 'user_id': user.id, 'username': user.username }
    pass
