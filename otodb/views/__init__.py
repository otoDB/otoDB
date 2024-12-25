from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *

from otodb.models import MediaSong, MediaWork, TagMain, WorkSource

from .forms import LoginForm, WorkForm
from .scrape_platform import video_info

from datetime import date

def index(request: HttpRequest):
    return render(request, "otodb/index.html", {
        "random_work": MediaWork.objects.random()
        }
    )

def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    sources = WorkSource.objects.filter(media=work)
    return render(request, "otodb/work.html", {'work':work, "sources": sources})

def tag(request: HttpRequest, tag_id: int):
    return render(request, "otodb/tag.html", {"work": TagMain.objects.get(pk=tag_id)})

SEARCH_TYPE_LOOKUP = {"work": MediaWork, "song": MediaSong, "tag": TagMain, "wiki": None}
def search(request: HttpRequest):
    type = request.GET.get('type')
    query = request.GET.get('query')
    results = SEARCH_TYPE_LOOKUP[type].objects.filter(title__contains=query)
    return render(request, "otodb/search.html", {"results": results})

@login_required
def profile(request: HttpRequest):
    return render(request, "otodb/profile.html")

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('otodb:index')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('otodb:index')
            form.add_error(None, "Authentication failed")
    else:
        form = LoginForm()

    return render(request, 'otodb/login.html', {"form": form})

def logout_view(request: HttpRequest):
    if request.user.is_authenticated:
        logout(request)
    return redirect('otodb:index')

def register_view(request: HttpRequest):
    return render(request, 'otodb/register.html')

@login_required
def new_work(request: HttpRequest):
    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            print(link)
            try:
                info = video_info(link)
                if info['site'].lower() not in ['niconico', 'bilibili', 'youtube', 'soundcloud']:
                    raise Exception(f"Site {info['site']} not supported")

                work = MediaWork(title=info['title'], description=info['description'])
                work.save()
                if 'tags' in info:
                    work.tags.add(*info['tags'])

                src = WorkSource(media=work, url=info['url'], published_date=date.fromtimestamp(info['timestamp']))
                src.save()

                return redirect('otodb:work', work_id=work.pk)
            except Exception as e:
                form.add_error(None, 'Error:' + str(e))

    else:
        form = WorkForm()

    return render(request, 'otodb/new_work.html', {'form': form})
