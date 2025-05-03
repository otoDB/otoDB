import string

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.shortcuts import redirect

from otodb.account.models import Account, Invitation


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = Account
        fields = ["username", "email"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Account
        fields = ["username", "email", "password", "is_active"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["username", "email"]
    list_filter = ["level"]
    fieldsets = [
        (None, {"fields": ["username", "email", "password"]}),
        ("Permissions", {"fields": ["level"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username", "email"]
    ordering = ["username"]
    filter_horizontal = []

class InvitationAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url="", extra_context=None):
        Invitation.objects.create(secret=get_random_string(16, string.ascii_letters+string.digits))
        return redirect('admin:account_invitation_changelist')

admin.site.register(Account, UserAdmin)
admin.site.register(Invitation, InvitationAdmin)
# Since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
