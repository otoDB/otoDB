from datetime import date

from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from yt_dlp import YoutubeDL

from otodb.models import MediaWork, WorkSource
from otodb.models.enums import Platform, WorkOrigin


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

        info['extractor'] = {
            'youtube': Platform.YOUTUBE,
            'bilibili': Platform.BILIBILI,
            'niconico': Platform.NICONICO,
            'soundcloud': Platform.SOUNDCLOUD,
        }.get(info['extractor'].lower())

        match info['extractor']:
            case Platform.YOUTUBE:
                info['webpage_url'] = f'https://youtu.be/{info['id']}'
            case Platform.BILIBILI:
                info['webpage_url'] = f'https://bilibili.com/video/{info['id']}/'
                info['tags'] = [tag[3:-1] if tag.startswith('发现《') and tag.endswith('》') else tag for tag in info['tags']]
            case Platform.NICONICO:
                info['webpage_url'] = f'https://nicovideo.jp/watch/{info['id']}'
            case Platform.SOUNDCLOUD:
                pass

        return { keys[key]: info[key] for key in keys if key in info }


class WorkForm(forms.ModelForm):
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'rating', 'thumbnail']

class ManualSourceForm(forms.ModelForm):
    class Meta:
        model = WorkSource
        fields = ['media', 'url', 'published_date', 'work_origin', 'work_status', 'work_width', 'work_height', 'platform']

class SourceSiteForm(forms.Form):
    link = forms.CharField(label='Link', required=True)
    official = forms.BooleanField(label='Is this an official upload?', required=False)

def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    sources = WorkSource.objects.filter(media=work)
    tags = work.tags.filter(aliased_to__isnull=True)
    return render(request, "works/work.html", {'work':work, "sources": sources, 'tags': tags})

def save_source(work, info, official):
    print(WorkSource.objects.filter(platform=info['site'], source_id=info['id']))
    if WorkSource.objects.filter(platform=info['site'], source_id=info['id']):
        raise Exception('This source already exists in the database.')

    src = WorkSource(media=work,
        url=info['url'], platform=info['site'], source_id=info['id'],
        published_date=date.fromtimestamp(info['timestamp']),
        work_origin=WorkOrigin(official),
        work_width=info.get('work_width',None), work_height=info.get('work_height',None))
    src.save()

@login_required
def new(request: HttpRequest):
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            official = form.cleaned_data['official']
            try:
                info = video_info(link)
                if info['site'] is None:
                    raise Exception('Site not supported')

                work = MediaWork(title=info['title'], description=info['description'], thumbnail=info.get('thumb', None))
                work.save()
                if 'tags' in info:
                    work.tags.add(*info['tags'])

                save_source(work, info, official)

                return redirect('otodb:work', work_id=work.id)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e))

    else:
        form = SourceSiteForm(initial={'official':True})

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
                if info['site'] is None:
                    raise Exception('Site not supported')

                if 'tags' in info:
                    work.tags.add(*info['tags'])

                save_source(work, info, official)

                return redirect('otodb:work', work_id=work.id)
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
            return redirect('otodb:work', work_id=work.id)

    else:
        form = WorkForm(instance=work)

    return render(request, 'works/edit.html', {'work': work, 'form': form})

@login_required
def set_tags(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)

    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            tags = [request.POST[f'tag-{i}'] for i in range(n)]
            work.tags.set(tags)
            work.save()

        except Exception as e:
            print(e)

    return redirect('otodb:work', work_id=work.id)
