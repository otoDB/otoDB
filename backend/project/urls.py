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

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from project import settings  # noqa: F811

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^", include("otodb.urls")),
]

if settings.DEBUG_TOOLBAR:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))

if not settings.OTODB_CDN_ENABLED:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
