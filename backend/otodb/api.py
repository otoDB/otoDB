from typing import List, Tuple

from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

from ninja import NinjaAPI, Schema, Router
from ninja.security import django_auth, django_auth_superuser

from otodb.models import WorkSource
from otodb.models.enums import Platform

api = NinjaAPI(urls_namespace="otodb:api", csrf=True)
auth = Router()
api.add_router('/auth/', auth)

class VideoQuery(Schema):
    rel: str
    tags: List[Tuple[str, str]]

class Error(Schema):
    message: str

class UserLogin(Schema):
    user_id: int
    username: str

@auth.get("/csrf")
def csrf(request):
    return {"csrf_token": get_token(request)}

@auth.post("/login", response={ 200: UserLogin, 401: Error })
def login_endpoint(request, username: str, password: str):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return { 'user_id': user.id, 'username': user.username }
    return 401, {'message': 'Login failed.'}

@auth.get("/status", response={ 200: UserLogin, 401: Error })
def status(request):
    print(request.user)
    if request.user.is_authenticated:
        return { 'user_id': request.user.id, 'username': request.user.username }
    return 401, {'message': 'Not logged in.'}

@auth.post("/logout", auth=django_auth)
def logout_endpoint(request):
    logout(request)
    return {'message': 'Logged out'}

@api.get("/query_video", response={ 200: VideoQuery, 404: Error })
def query_video(request, platform: str, id: str):
    try:
        work = WorkSource.objects.get(platform=Platform.from_str(platform), source_id=id)
    except WorkSource.DoesNotExist:
        return 404, {'message': 'Not in the database.'}

    media = work.media
    tags = list(media.tags.values_list('name', 'slug'))

    return {
        'tags': [(name, reverse('otodb:tag', kwargs={ 'tag_slug': slug })) for name, slug in tags],
        'rel': reverse('otodb:work', kwargs={ 'work_id': media.id })
        }
