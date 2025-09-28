from django.urls import path

from . import views
from .api import api

app_name = 'otodb'
urlpatterns = [
	path('api/', api.urls),
	path('chores/cookies', views.upload_cookies, name='upload_cookies'),
]
