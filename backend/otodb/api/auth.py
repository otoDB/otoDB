from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from ninja import Schema, Router
from ninja.security import django_auth

from .common import Error

auth_router = Router()

class UserLogin(Schema):
    user_id: int
    username: str

@auth_router.get("/csrf")
def csrf(request):
    return {"csrf_token": get_token(request)}

@auth_router.post("/login", response={ 200: UserLogin, 401: Error })
def login_endpoint(request, username: str, password: str):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return { 'user_id': user.id, 'username': user.username }
    return 401, {'message': 'Login failed.'}

@auth_router.get("/status", response={ 200: UserLogin, 401: Error })
def status(request):
    if request.user.is_authenticated:
        return { 'user_id': request.user.id, 'username': request.user.username }
    return 401, {'message': 'Not logged in.'}

@auth_router.post("/logout", auth=django_auth)
def logout_endpoint(request):
    logout(request)
    return {'message': 'Logged out'}
