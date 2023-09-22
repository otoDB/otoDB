from dotmap import DotMap
from django.conf import settings
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ___ import settings  # noqa: F811

def G(request):
    return DotMap({
        "config": settings.OTODB_CONFIG_DICT
    })
