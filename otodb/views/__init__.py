from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from random import choice

from otodb.models import MediaWork, TagMain, MediaSong, WorkSource


def index(request: HttpRequest):
    rand_work = MediaWork.objects.get(pk=choice(MediaWork.objects.values_list('pk', flat=True)))
    return render(request, "otodb/index.html", {"work": rand_work})

def work(request: HttpRequest, work_id: int):
    context = {
        "work": MediaWork.objects.get(pk=work_id),
    }
    context["sources"] = WorkSource.objects.filter(media=context["work"])
    return render(request, "otodb/work.html", context)

def tag(request: HttpRequest, tag_id: int):
    return render(request, "otodb/tag.html", {"work": TagBase.objects.get(pk=tag_id)})

SEARCH_TYPE_LOOKUP = {"work": MediaWork, "song": MediaSong, "tag": TagMain, "wiki": None}
def search(request: HttpRequest):
    type = request.GET.get('type')
    query = request.GET.get('query')
    results = SEARCH_TYPE_LOOKUP[type].objects.filter(title__contains=query)
    return render(request, "otodb/search.html", {"results": results})

def profile(request: HttpRequest):
    return render(request, "otodb/profile.html")

def login_view(request: HttpRequest):
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    if username is None or password is None:
        return render(request, "otodb/login.html")
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('otodb:index')
    else:
        return redirect('otodb:index')
    
def logout_view(request: HttpRequest):
    logout(request)
    return redirect('otodb:index')

