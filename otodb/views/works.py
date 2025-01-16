from datetime import date

from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from simple_history.template_utils import HistoricalRecordContextHelper
from simple_history.utils import update_change_reason

from yt_dlp import YoutubeDL

from otodb.models import MediaWork, WorkSource, TagWork
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
        if info.get('_type') == 'playlist':
            info = info['entries'][0] # todo need some work...

        info['extractor'] = Platform.from_str(info['extractor'])

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
        
        for c in ['?', '/']: # drop query strings and subdirectories
            if i := info['id'].find(c):
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

def add_tags_to_work(work: MediaWork, info):
    if 'tags' in info:
        work.tags.add(*info['tags'])

@login_required
def new(request: HttpRequest):
    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            is_reupload = not form.cleaned_data['official']
            try:
                info = video_info(link)
                if info['site'] is None:
                    raise Exception('Site not supported')

                if src := check_source_duplicates(info):
                    return redirect('otodb:work', work_id=src.media.id)

                # Save work
                work = MediaWork(title=info['title'], description=info['description'], thumbnail=info.get('thumb', None))
                work.save()

                add_tags_to_work(work, info)

                save_source(work, info, is_reupload)

                return redirect('otodb:work', work_id=work.id)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e)) # FIXME potentially dangerous if a deeper exception is caught (e.g. from the DB)

    else:
        form = SourceSiteForm(initial={'official':True})

    return render(request, 'works/new.html', {'form': form, 'title': 'New work'})

@login_required
def new_source(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)

    if request.method == 'POST':
        form = SourceSiteForm(request.POST)
        if form.is_valid():
            link = form.cleaned_data['link']
            is_reupload = not form.cleaned_data['official']
            try:
                info = video_info(link)
                if info['site'] is None:
                    raise Exception('Site not supported')

                add_tags_to_work(work, info)
                
                if src := check_source_duplicates(info):
                    if src.media.id != work.id:
                        raise Exception(f'This source already belongs to a different work ({work.id} - {work}). Consider merging works.')
                    else:
                        return redirect('otodb:work', work_id=work.id)

                
                save_source(work, info, is_reupload)

                return redirect('otodb:work', work_id=work.id)
            except Exception as e:
                form.add_error(None, 'Error: ' + str(e)) # FIXME potentially dangerous if a deeper exception is caught (e.g. from the DB)

    else:
        form = SourceSiteForm()

    return render(request, 'works/new.html', {'form': form, 'title': f'New source for "{work.title}"'})

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
            record.history_delta_changes = HistoricalRecordContextHelper(MediaWork, prev).context_for_delta_changes(delta)

            def int_list_str_to_list_of_int(s):
                return [ss.strip() for ss in s[1:-1].split(',') if ss.strip() != '']
            for rec in record.history_delta_changes:
                if rec['field'] == 'Tags': # FIXME this is horrible?
                    rec['old'] = str([str(TagWork.objects.get(id=int(id_))) for id_ in int_list_str_to_list_of_int(rec['old'])])
                    rec['new'] = str([str(TagWork.objects.get(id=int(id_))) for id_ in int_list_str_to_list_of_int(rec['new'])])
        history.append(record)
    history.reverse()
    return render(request, 'works/history.html', { 'work': work, 'history': history })
