from django.urls import path

from . import views
from .api import api
from .sitemap import sitemap

app_name = 'otodb'
urlpatterns = [
	path('sitemap.xml', sitemap, name='sitemap'),
	path('api/', api.urls),
	path('chores', views.chores, name='chores'),
	path('chores/cookies', views.upload_cookies, name='upload_cookies'),
	path('chores/roles', views.set_user_role, name='set_user_role'),
	path('auth_forward', views.auth_forward),
]
