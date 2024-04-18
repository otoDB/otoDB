from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Account


class UserAdmin(BaseUserAdmin):
    base_fieldsets = BaseUserAdmin.fieldsets
    fieldsets = base_fieldsets + (  # type: ignore
        (None, {
            "fields": (
                'email_activated',
                'is_deleted',
            ),
        }),
    )


admin.site.register(Account, UserAdmin)
