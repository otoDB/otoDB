from django.contrib import admin

from .models import WikiPage

admin.site.register([
    WikiPage
])
