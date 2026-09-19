from django import forms
from django.conf import settings
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from otodb.account.models import Account
from otodb.api.common import AuthedHttpRequest
from otodb.common import reset_cookies


def chores(request: AuthedHttpRequest):
	if not (request.user.is_authenticated and request.user.is_mod):
		return HttpResponse(status=403)
	return render(request, 'chores.html')


class UploadForm(forms.Form):
	file = forms.FileField()


@staff_member_required
def upload_cookies(request: HttpRequest):
	if request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)
		if form.is_valid():
			with open(settings.COOKIES_FILE, 'ab+') as destination:
				destination.writelines(request.FILES['file'].chunks())
			reset_cookies(settings.COOKIES_FILE)
			return redirect('/')
	else:
		form = UploadForm()

	return render(request, 'upload_cookies.html', {'form': form})


def auth_forward(request: HttpRequest):
	user = request.user
	if not user.is_authenticated:
		return HttpResponse(status=401)
	response = HttpResponse(status=204)
	response['X-User-ID'] = str(user.id)
	response['X-User-Name'] = user.username
	response['X-User-Role'] = 'admin' if user.is_mod else 'editor'
	return response


# Temporary chore view for restricting users below.
# To later be added to the main frontend.


class SetUserRoleForm(forms.Form):
	username = forms.CharField(max_length=127)
	role = forms.ChoiceField(
		choices=[
			(Account.Levels.RESTRICTED, 'Restricted'),
			(Account.Levels.MEMBER, 'Member'),
		],
		initial=Account.Levels.RESTRICTED,
	)


def set_user_role(request: AuthedHttpRequest):
	if not (request.user.is_authenticated and request.user.is_mod):
		return HttpResponse(status=403)

	form = SetUserRoleForm(request.POST or None)
	message = None
	if form.is_valid():
		target = Account.objects.filter(
			username__iexact=form.cleaned_data['username']
		).first()
		if target is None:
			form.add_error('username', 'No user with that username')
		elif request.user.level <= target.level:
			form.add_error('username', "You can't change this user's role")
		else:
			target.level = int(form.cleaned_data['role'])
			target.save(update_fields=['level'])
			label = Account.Levels(target.level).label
			LogEntry.objects.log_actions(
				user_id=request.user.id,
				queryset=[target],
				action_flag=CHANGE,
				change_message=f'Set role to {label} via mod chore',
			)
			message = f'Set {target.username} to {label}'
			form = SetUserRoleForm()

	return render(request, 'set_user_role.html', {'form': form, 'message': message})
