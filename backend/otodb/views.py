from django import forms
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from otodb.common import reset_ydl

class UploadForm(forms.Form):
    file = forms.FileField()

@staff_member_required
def upload_youtube_cookies(request: HttpRequest):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            with open(settings.YOUTUBE_COOKIES_FILE, "wb+") as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            reset_ydl(settings.YOUTUBE_COOKIES_FILE)
            return redirect('/')
    else:
        form = UploadForm()

    return render(request, 'upload_youtube_cookies.html', { 'form': form })
