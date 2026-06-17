from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from otodb.common import reset_cookies


class UploadForm(forms.Form):
	file = forms.FileField()


@staff_member_required
def upload_cookies(request: HttpRequest):
	if request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)
		if form.is_valid():
			with open(settings.COOKIES_FILE, 'ab+') as destination:
				for chunk in request.FILES['file'].chunks():
					destination.write(chunk)
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
