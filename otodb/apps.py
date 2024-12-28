from django.apps import AppConfig


class OtodbConfig(AppConfig):
    name = 'otodb'

    def ready(self):
        from . import signals  # connect @receivers
