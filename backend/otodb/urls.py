from django.urls import include, path

from . import views
from .api import api
from .sitemap import sitemap

app_name = 'otodb'
urlpatterns = [
	path('sitemap.xml', sitemap, name='sitemap'),
	path('api/', api.urls),
	path('chores/cookies', views.upload_cookies, name='upload_cookies'),
	path('django-rq/', include('django_rq.urls')),
]
