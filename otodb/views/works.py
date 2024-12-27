from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *
from django import forms

from otodb.models import MediaWork, WorkSource
from otodb.models.sources import SourceWorkBilibili, SourceWorkNiconico, SourceWorkSoundCloud, SourceWorkYouTube, SourceWorkBase
from otodb.models.enums import WorkOrigin, WorkStatus

from datetime import date

from yt_dlp import YoutubeDL

def video_info(link):
    keys = {
            'extractor': 'site',
            'title': 'title',
            'description': 'description',
            'tags': 'tags',
            'width': 'work_width',
            'height': 'work_height',
            'webpage_url': 'url',
            'id': 'id',
            'thumbnail': 'thumb',
            'timestamp':  'timestamp'
        }
    with YoutubeDL({'http_headers': {'Accept-Language': 'ja'}}) as ydl:
        info = ydl.extract_info(link, download=False)
        if info.get('_type') == 'playlist':
            info = info['entries'][0] # todo need some work...
        info['extractor'] = info['extractor'].lower()
        if info['extractor'] == 'bilibili':
            info['tags'] = [tag[3:-1] if tag.startswith('发现《') and tag.endswith('》') else tag for tag in info['tags']]
        match info['extractor']:
            case 'youtube':
                info['webpage_url'] = f'https://youtu.be/{info['id']}'
            case 'bilibili':
                info['webpage_url'] = f'https://bilibili.com/video/{info['id']}/'
            case 'niconico':
                info['webpage_url'] = f'https://nicovideo.jp/watch/{info['id']}'
            case 'soundcloud':
                pass

        return { keys[key]: info[key] for key in keys if key in info }


class WorkForm(forms.ModelForm):
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'rating', 'thumbnail']

class ManualSourceForm(forms.ModelForm):
    class Meta:
        model = WorkSource
        fields = ['media', 'url', 'published_date', 'work_origin', 'work_status', 'work_width', 'work_height']

class SourceSiteForm(forms.Form):
    link = forms.CharField(label='Link', required=True)
    official = forms.BooleanField(label='Is this an official upload?', required=False)

def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    sources = WorkSource.objects.filter(media=work)
    sources = [SourceWorkBase.objects.get_subclass(work_source=src) for src in sources]
    tags = work.tags.filter(aliased_to__isnull=True)
    return render(request, "works/work.html", {'work':work, "sources": sources, 'tags': tags})

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
def new(request: HttpRequest):
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

    return render(request, 'works/new.html', {'form': form})

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

    return render(request, 'works/new_source.html', {'form': form, 'work': work})

@login_required
def edit(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    if request.method == 'POST':
        form = WorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect('otodb:work', work_id=work.pk)

    else:
        form = WorkForm(instance=work)

    return render(request, 'works/edit.html', {'work': work, 'form': form})

@login_required
def set_tags(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)

    error = None
    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            tags = [request.POST[f'tag-{i}'] for i in range(n)]
            work.tags.set(tags)
            work.save()

        except Exception as e:
            print(e)

    return redirect('otodb:work', work_id=work.pk)
