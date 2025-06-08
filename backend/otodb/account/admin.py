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
    level = forms.ChoiceField(choices=[c for c in Account.Levels.choices if c[0] < Account.Levels.ADMIN], initial=Account.Levels.MEMBER)

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
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.level > obj.level

class AddInvitationForm(forms.ModelForm):
    bulk = forms.IntegerField(initial=1, min_value=1)
    level = forms.ChoiceField(choices=[c for c in Account.Levels.choices if c[0] < Account.Levels.ADMIN], initial=Account.Levels.MEMBER)
    class Meta:
        model = Invitation
        fields = ["level"]

class InvitationAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = AddInvitationForm
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields['level'].initial = 20
        return form

    def add_view(self, request, form_url="", extra_context=None):
        if request.method == "POST":
            form = AddInvitationForm(request.POST)
            if form.is_valid():
                for _ in range(form.cleaned_data['bulk']):
                    Invitation.objects.create(
                        secret=get_random_string(16, string.ascii_letters+string.digits),
                        level=form.cleaned_data['level']
                        )
                return redirect('admin:account_invitation_changelist')
        return super().add_view(request, form_url, extra_context)

admin.site.register(Account, UserAdmin)
admin.site.register(Invitation, InvitationAdmin)
# Since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
