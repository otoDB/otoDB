from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *

from otodb.models import MediaSong, MediaWork, TagMain, WorkSource, Pool
from otodb.models.sources import SourceWorkBilibili, SourceWorkNiconico, SourceWorkSoundCloud, SourceWorkYouTube, SourceWorkBase
from otodb.models.enums import WorkOrigin, WorkStatus
from otodb.account.models import Account

from .forms import *
from .scrape_platform import video_info

from datetime import date
import json

def index(request: HttpRequest):
    return render(request, "index.html", {
        "random_work": MediaWork.objects.random()
        }
    )

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
    return render(request, "search.html", {"results": results, "type": search_type, 'query': query})

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

    return render(request, 'user/login.html', {"form": form})

@login_required
def logout_view(request: HttpRequest):
    logout(request)
    return redirect('otodb:index')

def register_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('otodb:index')
    return render(request, 'user/register.html')

def profile(request: HttpRequest, user_id: int):
    user = get_object_or_404(Account, pk=user_id)
    return render(request, "user/profile.html", {'view_user': user})

def user_lists(request: HttpRequest, user_id: int):
    lists = Pool.objects.filter(author__pk=user_id)
    return render(request, 'user/user_lists.html', {'lists': lists})

def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    sources = WorkSource.objects.filter(media=work)
    sources = [SourceWorkBase.objects.get_subclass(work_source=src) for src in sources]
    return render(request, "work/work.html", {'work':work, "sources": sources})

ACCEPT_SITES = {'niconico': SourceWorkNiconico, 'bilibili': SourceWorkBilibili, 'youtube': SourceWorkYouTube, 'soundcloud': SourceWorkSoundCloud}
def save_source(work, info, official):
    if ACCEPT_SITES[info['site']].objects.filter(source_id=info['id']):
        raise Exception('This source already exists in the database.')

    src = WorkSource(media=work,
        url=info['url'],
        published_date=date.fromtimestamp(info['timestamp']),
        work_origin=WorkOrigin.AUTHOR if official else WorkOrigin.REUPLOAD,
        work_width=info.get('work_width',None), work_height=info.get('work_height',None))
    src.save()

    site_src = ACCEPT_SITES[info['site']](work_source=src, source_id=info['id'])
    site_src.save()

@login_required
def new_work(request: HttpRequest):
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            official = form.cleaned_data['official']
            try:
                info = video_info(link)
                if info['site'] not in ACCEPT_SITES:
                    raise Exception(f"Site {info['site']} not supported")

                work = MediaWork(title=info['title'], description=info['description'], thumbnail=info.get('thumb', None))
                work.save()
                if 'tags' in info:
                    work.tags.add(*info['tags'])

                save_source(work, info, official)

                return redirect('otodb:work', work_id=work.pk)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e))

    else:
        form = SourceSiteForm()

    return render(request, 'work/new_work.html', {'form': form})

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

                save_source(work, info, official)

                return redirect('otodb:work', work_id=work.pk)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e))

    else:
        form = SourceSiteForm()

    return render(request, 'work/new_source.html', {'form': form, 'work': work})

@login_required
def attach_tag(request: HttpRequest, work_id: int): # todo
    work = get_object_or_404(MediaWork, pk=work_id)
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():

            return redirect('otodb:work', work_id=work.pk)
    else:
        form = SourceSiteForm()

    return render(request, 'work/attach_tag.html', {'work': work})

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

    return render(request, 'work/edit_work.html', {'work': work, 'form': form})

def tag(request: HttpRequest, tag_id: int):
    tag = get_object_or_404(TagMain, pk=tag_id)
    works = MediaWork.objects.filter(tags__id=tag_id)
    return render(request, "tag/tag.html", {"tag": tag, "works": works})

def list(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    works = PoolItem.objects.filter(pool=l).select_related('work').order_by('order')
    return render(request, "list/list.html", {"list": l, 'works': works})

@login_required
def new_list(request: HttpRequest):
    if request.method == 'POST':
        form = ListForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['description']
            stat = form.cleaned_data['status']

            l = Pool(name=name, description=desc, status=stat, author=request.user)
            l.save()

            return redirect('otodb:list', list_id=l.pk)

    else:
        form = ListForm()

    return render(request, 'list/new_list.html', {'form': form})

@login_required
def list_edit(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    if l.author != request.user:
        return redirect('otodb:list', list_id=l.pk)

    error = None
    if request.method == 'POST':
        list_form = ListForm(request.POST, instance=l)
        if list_form.is_valid():
            name = list_form.cleaned_data['name']
            desc = list_form.cleaned_data['description']
            stat = list_form.cleaned_data['status']
            l.name = name
            l.description = desc
            l.status = stat
            l.save()
        try:
            sz = int(request.POST['size'])
            new_entries = [(i, int(request.POST[f'work-{i}']), request.POST[f'desc-{i}']) for i in range(sz)]
            PoolItem.objects.filter(pool=l).delete()
            for i, wk, desc in new_entries:
                PoolItem(work_id=wk, description=desc, order=i, pool=l).save()

            return redirect('otodb:list', list_id=l.pk)
        except Exception as e:
            error = str(e)
    else:
        list_form = ListForm(instance=l)

    return render(request, "list/edit.html", {"list": l, 'error': error, 'list_form': list_form})

@login_required
def list_delete(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    if l.author != request.user:
        return redirect('otodb:list', list_id=l.pk)

    l.delete()

    return redirect("otodb:user_lists", user_id=request.user.id)
