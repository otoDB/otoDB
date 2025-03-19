from django.urls import path

from . import views
from .api import api

app_name = "otodb"
urlpatterns = [
    path("api/", api.urls),
    path("upload_youtube_cookies", views.upload_youtube_cookies, name="upload_youtube_cookies"),
]
