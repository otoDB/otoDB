"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from typing import TYPE_CHECKING

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

if TYPE_CHECKING:
	from project import settings  # noqa: F811

urlpatterns = [
	path('admin/', admin.site.urls),
	re_path(r'^', include('otodb.urls')),
]

if settings.DEBUG:
	urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

if not settings.OTODB_CDN_ENABLED:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
