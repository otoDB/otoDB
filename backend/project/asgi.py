"""
ASGI config for project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from otodb_next.middleware import AnonymousEdgeCacheMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = AnonymousEdgeCacheMiddleware()(get_asgi_application())
