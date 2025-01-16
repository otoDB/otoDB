from datetime import date

from django import forms
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404, redirect, render

# from simple_history.template_utils import HistoricalRecordContextHelper
from simple_history.utils import update_change_reason

from yt_dlp import YoutubeDL

from otodb.common import get_diff
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
    with YoutubeDL({'http_headers': {'Accept-Language': 'ja'}, 'noplaylist': True}) as ydl:
        info = ydl.extract_info(link, download=False)
        print(info)
        if info.get('_type') == 'playlist':
            info = info['entries'][0] # todo need some work...

        info['extractor'] = Platform.from_str(info['extractor'])

        match info['extractor']:
            case Platform.YOUTUBE:
                info['webpage_url'] = f'https://youtu.be/{info['id']}'
            case Platform.BILIBILI:
                info['webpage_url'] = f'https://www.bilibili.com/video/{info['id']}/'
                info['tags'] = [tag[3:-1] if tag.startswith('发现《') and tag.endswith('》') else tag for tag in info['tags']]
            case Platform.NICONICO:
                info['webpage_url'] = f'https://nicovideo.jp/watch/{info['id']}'
            case Platform.SOUNDCLOUD:
                pass # TODO
        
        for c in ['?', '/']: # drop query strings and subdirectories
            i = info['id'].find(c)
            if i != -1:
                info['id'] = info['id'][:i]

        return { keys[key]: info[key] for key in keys if key in info }


class WorkEditForm(forms.ModelForm):
    reason = forms.CharField(label="Update Reason", required=True)
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
    work_id = forms.IntegerField(widget=forms.HiddenInput(), initial=-1)

class SourceCheckinForm(forms.Form):
    official = forms.BooleanField(label='Is this an official upload?', required=False)
    work_id = forms.IntegerField(widget=forms.HiddenInput(), initial=-1)

def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    return render(request, "works/work.html", {'work':work})

def check_source_duplicates(info):
    query = WorkSource.objects.filter(platform=info['site'], source_id=info['id'])
    if query.exists():
        return query.first()
        
def save_source(work: MediaWork, info, is_reupload: bool):
    src = WorkSource(media=work, title=info['title'], description=info['description'],
        url=info['url'], platform=info['site'], source_id=info['id'],
        published_date=date.fromtimestamp(info['timestamp']),
        work_origin=WorkOrigin(is_reupload), thumbnail=info.get('thumb', None),
        work_width=info.get('work_width',None), work_height=info.get('work_height',None))
    src.save()
    return src

def add_tags_to_work(work: MediaWork, info):
    if 'tags' in info:
        work.tags.add(*info['tags'])

@login_required
def check_in_source(request: HttpRequest, source_id: int):
    src = get_object_or_404(WorkSource, pk=source_id)
    title = f'Checking-in source {src.title}'
    suggestions = None # used in case we want to prompt adding source to an existing work instead of a new work

    if src.media is not None:
        raise Http404("Source is already bound.")

    if request.method == 'POST':
        form = SourceCheckinForm(request.POST)
        if form.is_valid():
            is_reupload = not form.cleaned_data['official']
            work_id = form.cleaned_data['work_id']
            if work_id > 0:
                work = get_object_or_404(MediaWork, pk=work_id)
                title += f' for "{work.title}"'
            else:
                work = MediaWork(title=src.title, description=src.description, thumbnail=src.thumbnail)
                work.save()
            
            # FIXME this double ping will do for now.. I don't want to store tags on sources
            add_tags_to_work(work, video_info(src.url))

            src.media = work
            src.work_origin = WorkOrigin(is_reupload)
            src.save()

            return redirect('otodb:work', work_id=work.id)
    else:
        work_id = request.GET.get('work_id')
        form = SourceCheckinForm(initial={ 'official': not src.work_origin })
        if work_id and int(work_id) > 0:
            work_id = int(work_id)
            work = get_object_or_404(MediaWork, pk=work_id)
            title += f' for "{work.title}"'
            form.fields["work_id"].initial = work_id
        else:
            suggestions = MediaWork.objects.filter(title__contains=src.title)[:3]

    return render(request, 'works/check_in_source.html', {'form': form, 'source': src, 'title': title, 'suggestions': suggestions})

@login_required
def new(request: HttpRequest):
    title = 'New work'
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            is_reupload = not form.cleaned_data['official']
            work_id = form.cleaned_data['work_id']
            work = None
            if work_id > 0:
                work = get_object_or_404(MediaWork, pk=work_id)
                title = f'New source for "{work.title}"'
            try:
                info = video_info(link)
                if info['site'] is None:
                    raise Exception('Site not supported')

                src = check_source_duplicates(info)
                if not src: # src does not exist
                    src = save_source(None, info, is_reupload)
                elif src.media: # src exists and is already bound to a work
                    if not work:
                        return redirect('otodb:work', work_id=src.media.id)
                    elif src.media.id != work_id:
                        raise Exception(f'This source already belongs to a different work ({work.id} - {work}). Consider merging works.')
                    else:
                        return redirect('otodb:work', work_id=work.id)

                if work:
                    return redirect(reverse('otodb:work_check_in_source', kwargs={'source_id':src.id}) + f'?work_id={work_id}')
                else:
                    return redirect('otodb:work_check_in_source', source_id=src.id)
            except Exception as e:
                # FIXME potentially dangerous to send this to client if a deeper exception is caught (e.g. from the DB)
                form.add_error(None, 'Error: ' + str(e))
    else:
        if url := request.GET.get('url'):
            form = SourceSiteForm(initial={ 'link': url })
        elif work_id := request.GET.get('work_id'):
            work_id = int(work_id)
            form = SourceSiteForm(initial={ 'work_id': work_id })
            work = get_object_or_404(MediaWork, pk=work_id)
            title = f'New source for "{work.title}"'
        else:
            form = SourceSiteForm(initial={ 'official': True })
        
    return render(request, 'works/new.html', {'form': form, 'title': title})

@login_required
def edit(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    if request.method == 'POST':
        form = WorkEditForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            update_change_reason(work, form.cleaned_data['reason'])
            return redirect('otodb:work', work_id=work.id)

    else:
        form = WorkEditForm(instance=work)

    return render(request, 'works/edit.html', {'work': work, 'form': form})

@login_required
def set_tags(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)

    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            tags = [request.POST[f'tag-{i}'] for i in range(n)]
            work.tags.set_tag_list(tags)
            work.tags.save()

        except Exception as e:
            print(e)

    return redirect('otodb:work', work_id=work.id)

@login_required
def merge(request: HttpRequest):
    if request.method == 'POST':
        try:
            work_a = request.POST['left']
            work_b = request.POST['right']

            title = request.POST['title']
            description = request.POST['description']
            thumbnail = request.POST['thumbnail']
            rating = request.POST['rating']

            work_a = MediaWork.objects.get(id=work_a)
            work_b = MediaWork.objects.get(id=work_b)

            work_a.title = title
            work_a.description = description
            work_a.thumbnail = thumbnail 
            work_a.rating = rating
            work_a.tags.add(*work_b.tags.all())
            work_a.save()

            for src in work_b.worksource_set.all():
                src.media = work_a
                src.save()

            work_b.delete()

            return redirect('otodb:work', work_id=work_a.id)        
        except Exception as e:
            print(e)

    return render(request, 'works/merge.html')

def history(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    
    history = []
    for record in work.history.all().reverse():
        if history != []:
            prev = history[-1]
            delta = record.diff_against(prev)
            record.history_delta_changes = get_diff(delta)
        history.append(record)
    history.reverse()
    return render(request, 'works/history.html', { 'work': work, 'history': history })
