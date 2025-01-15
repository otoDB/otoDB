from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from project import settings  # noqa: F811


def G(request):
    return {
        "config": settings.OTODB_CONFIG_DICT
    }
