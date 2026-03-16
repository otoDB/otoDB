"""
WSGI config for project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()

if trusted_hosts := os.environ.get('OTODB_TRUSTED_PROXY_HOSTS'):
	from granian.utils.proxies import wrap_wsgi_with_proxy_headers

	application = wrap_wsgi_with_proxy_headers(
		application,
		trusted_hosts=[h.strip() for h in trusted_hosts.split(',')],
	)
