from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *

from otodb.models import MediaSong, MediaWork, TagMain, WorkSource, Pool
from otodb.models.sources import SourceWorkBilibili, SourceWorkNiconico, SourceWorkSoundCloud, SourceWorkYouTube, SourceWorkBase
from otodb.models.enums import WorkOrigin, WorkStatus
from otodb.account.models import Account

from .forms import LoginForm, WorkForm, SourceSiteForm, NewListForm
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
    sources = [SourceWorkBase.objects.get_subclass(work_source=src) for src in sources]
    return render(request, "otodb/work.html", {'work':work, "sources": sources})

def tag(request: HttpRequest, tag_id: int):
    tag = get_object_or_404(TagMain, pk=tag_id)
    works = MediaWork.objects.filter(tags__id=tag_id)
    return render(request, "otodb/tag.html", {"tag": tag, "works": works})

SEARCH_TYPE_LOOKUP = {
    "work": lambda q: MediaWork.objects.filter(title__contains=q),
    "song": lambda q: MediaSong.objects.filter(title__contains=q),
    "tag":  lambda q:TagMain.objects.filter(name__contains=q),
    "wiki": None
}
def search(request: HttpRequest):
    search_type = request.GET.get('type')
    query = request.GET.get('query')
    results = SEARCH_TYPE_LOOKUP[search_type](query)
    return render(request, "otodb/search.html", {"results": results, "type": search_type, 'query': query})

def profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return render(request, "otodb/profile.html", {'view_user': user})

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('otodb:index')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
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

@login_required
def logout_view(request: HttpRequest):
    logout(request)
    return redirect('otodb:index')

def register_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('otodb:index')
    return render(request, 'otodb/register.html')

ACCEPT_SITES = {'niconico': SourceWorkNiconico, 'bilibili': SourceWorkBilibili, 'youtube': SourceWorkYouTube, 'soundcloud': SourceWorkSoundCloud}
@login_required
def new_work(request: HttpRequest):
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            try:
                info = video_info(link)
                if info['site'] not in ACCEPT_SITES:
                    raise Exception(f"Site {info['site']} not supported")

                work = MediaWork(title=info['title'], description=info['description'], thumbnail=info.get('thumb', None))
                work.save()
                if 'tags' in info:
                    work.tags.add(*info['tags'])

                src = WorkSource(media=work, url=info['url'], published_date=date.fromtimestamp(info['timestamp']))
                src.save()

                site_src = ACCEPT_SITES[info['site']](work_source=src, source_id=info['id'])
                site_src.save()

                return redirect('otodb:work', work_id=work.pk)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e))

    else:
        form = SourceSiteForm()

    return render(request, 'otodb/new_work.html', {'form': form})

@login_required
def new_source(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)

    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            official = form.cleaned_data['official']
            try:
                info = video_info(link)
                if info['site'] not in ACCEPT_SITES:
                    raise Exception(f"Site {info['site']} not supported")

                if 'tags' in info:
                    work.tags.add(*info['tags'])

                sources = ACCEPT_SITES[info['site']].objects.filter(work_source__in=WorkSource.objects.filter(media=work))
                print ([src.source_id for src in sources])
                if any(src.source_id == info['id'] for src in sources):
                    raise Exception('This source already exists for this work')

                src = WorkSource(media=work, url=info['url'], published_date=date.fromtimestamp(info['timestamp']), work_origin=WorkOrigin.AUTHOR if official else WorkOrigin.REUPLOAD)
                src.save()

                site_src = ACCEPT_SITES[info['site']](work_source=src, source_id=info['id'])
                site_src.save()

                return redirect('otodb:work', work_id=work.pk)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e))

    else:
        form = SourceSiteForm()

    return render(request, 'otodb/new_source.html', {'form': form, 'work': work})

@login_required
def attach_tag(request: HttpRequest, work_id: int): # todo
    work = get_object_or_404(MediaWork, pk=work_id)
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():

            return redirect('otodb:work', work_id=work.pk)
    else:
        form = SourceSiteForm()

    return render(request, 'otodb/attach_tag.html', {'work': work})

@login_required
def edit_work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    if request.method == 'POST':
        form = WorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect('otodb:work', work_id=work.pk)

    else:
        form = WorkForm(instance=work)

    return render(request, 'otodb/edit_work.html', {'work': work, 'form': form})

def user_lists(request: HttpRequest, user_id: int):
    lists = Pool.objects.filter(author__pk=user_id)
    return render(request, 'otodb/user_lists.html', {'lists': lists})

@login_required
def new_list(request: HttpRequest):
    if request.method == 'POST':
        form = NewListForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['description']
            stat = form.cleaned_data['status']

            l = Pool(name=name, description=desc, status=stat, author=request.user)
            l.save()

            return redirect('otodb:list', list_id=l.pk)

    else:
        form = NewListForm()

    return render(request, 'otodb/new_list.html', {'form': form})

def list(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    return render(request, "otodb/list.html", {"list": l})

def list_add_work(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    if request.method == 'POST':
        form = ListAddWorkForm(request.POST)
        if form.is_valid():
            work = form.cleaned_data['work']
            desc = form.cleaned_data['description']

            item = PoolItem(work__pk=work, description=desc)
            item.save()
            l.works

            return redirect('otodb:list', list_id=list_id)
    else:
        form = ListAddWorkForm()

    return render(request, "otodb/list_add_work.html", {"list": l})
