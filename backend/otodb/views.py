from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
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
