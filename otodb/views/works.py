from datetime import date

from django import forms
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404, redirect, render

from simple_history.utils import update_change_reason

from otodb.common import get_diff, video_info
from otodb.models import MediaWork, WorkSource, WorkRelation
from otodb.models.enums import WorkOrigin, WorkRelationTypes

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

def get_work_by_id(work_id: int):
    work = get_object_or_404(MediaWork, pk=work_id)
    if work.moved_to is not None:
        raise Exception('This work has been moved. Operation is invalid.')
    return work
    
def check_source_duplicates(info):
    query = WorkSource.objects.filter(platform=info['site'], source_id=info['id'])
    if query.exists():
        return query.first()

def add_tags_to_work(work: MediaWork, info):
    if 'tags' in info:
        work.tags.add(*info['tags'])

def work(request: HttpRequest, work_id: int):
    work = get_work_by_id(work_id)
    return render(request, "works/work.html", {'work':work})

@login_required
def check_in_source(request: HttpRequest, source_id: int):
    src = get_object_or_404(WorkSource, pk=source_id)
    title = f'Checking-in source "{src.title}"'
    suggestions = None # used in case we want to prompt adding source to an existing work instead of a new work
    work_id = -1

    if src.media is not None:
        raise Http404("Source is already bound.")

    if request.method == 'POST':
        form = SourceCheckinForm(request.POST)
        if form.is_valid():
            is_reupload = not form.cleaned_data['official']
            if w_id := request.POST.get('work_id'):
                work_id = int(w_id)
            if work_id > 0:
                work = get_work_by_id(work_id)
                title += f' for "{work.title}"'
            else:
                work = MediaWork(title=src.title, description=src.description, thumbnail=src.thumbnail)
                work.save()
            
            add_tags_to_work(work, video_info(src.url))

            src.media = work
            src.work_origin = WorkOrigin(is_reupload)
            src.save()

            return redirect('otodb:work', work_id=work.id)
    else:
        if w_id := request.GET.get('work_id'):
            work_id = int(w_id)
        form = SourceCheckinForm(initial={ 'official': not src.work_origin })
        if work_id > 0:
            work_id = int(work_id)
            work = get_work_by_id(work_id)
            title += f' for "{work.title}"'
        else:
            suggestions = MediaWork.objects.filter(title__contains=src.title, moved_to__isnull=True)[:3]

    return render(request, 'works/check_in_source.html', {'form': form, 'source': src, 'title': title, 'suggestions': suggestions, 'work_id': work_id})

def save_source(work: MediaWork, link: str, is_reupload: bool):
    info = video_info(link)
    if info['site'] is None:
        raise Exception('Site not supported')

    src = check_source_duplicates(info)
    if not src: # src does not exist
        src = WorkSource(media=work, title=info['title'], description=info['description'],
            url=info['url'], platform=info['site'], source_id=info['id'],
            published_date=date.fromtimestamp(info['timestamp']),
            work_origin=WorkOrigin(is_reupload), thumbnail=info.get('thumb', None),
            work_width=info.get('work_width',None), work_height=info.get('work_height',None))
        src.save()
    elif src.media: # src exists and is already bound to a work
        if not work:
            return redirect('otodb:work', work_id=src.media.id)
        elif src.media.id != work.id:
            raise Exception(f'This source already belongs to a different work ({work.id} - {work}). Consider merging works.')
        else:
            return redirect('otodb:work', work_id=work.id)

    if work:
        return redirect(reverse('otodb:work_check_in_source', kwargs={'source_id':src.id}) + f'?work_id={work.id}')
    else:
        return redirect('otodb:work_check_in_source', source_id=src.id)

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
                work = get_work_by_id(work_id)
                title = f'New source for "{work.title}"'
            try:
                return save_source(work, link, is_reupload)
            except Exception as e:
                # FIXME potentially dangerous to send this to client if a deeper exception is caught (e.g. from the DB)
                form.add_error(None, 'Error: ' + str(e))
    else:
        if url := request.GET.get('url'):
            form = SourceSiteForm(initial={ 'link': url })
            try:
                return save_source(None, url, False)
            except Exception as e:
                # FIXME potentially dangerous to send this to client if a deeper exception is caught (e.g. from the DB)
                form.add_error(None, 'Error: ' + str(e))
        elif work_id := request.GET.get('work_id'):
            work_id = int(work_id)
            form = SourceSiteForm(initial={ 'work_id': work_id })    
            work = get_work_by_id(work_id)

            title = f'New source for "{work.title}"'
        else:
            form = SourceSiteForm(initial={ 'official': True })
        
    return render(request, 'works/new.html', {'form': form, 'title': title})

@login_required
def edit(request: HttpRequest, work_id: int):
    work = get_work_by_id(work_id)
    relations = WorkRelation.get_relations_including_works([work])

    if request.method == 'POST':
        form = WorkEditForm(request.POST, instance=work)
        if form.has_changed() and form.is_valid():
            form.save()
            update_change_reason(work, form.cleaned_data['reason'])
            return redirect('otodb:work', work_id=work.id)

    else:
        form = WorkEditForm(instance=work)

    return render(request, 'works/edit.html', {'work': work, 'form': form, 'relations': relations, 'relation_types': WorkRelationTypes})

@login_required
def edit_relations(request: HttpRequest, work_id: int):
    work = get_work_by_id(work_id)

    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            new_relations = [(int(request.POST[f'relation-{i}']), int(request.POST[f'work-{i}']), bool(int(request.POST[f'direction-{i}']))) for i in range(n)]
            new_relations = [WorkRelation(B_id=work_id, A_id=w, relation=r) if d else WorkRelation(A_id=work_id, B_id=w, relation=r) for r, w, d in new_relations]
            
            old_relations = WorkRelation.get_relations_including_works([work])
            for r in old_relations:
                r.delete()
            for r in new_relations:
                r.save()

        except Exception as e:
            print(e)

    return redirect('otodb:work_relations', work_id=work.id)

@login_required
def set_tags(request: HttpRequest, work_id: int):
    work = get_work_by_id(work_id)

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

            work_a = MediaWork.objects.get(id=work_a, moved_to__isnull=True)
            work_b = MediaWork.objects.get(id=work_b, moved_to__isnull=True)

            work_a.title = title
            work_a.description = description
            work_a.thumbnail = thumbnail 
            work_a.rating = rating
            work_a.tags.add(*work_b.tags.all())
            work_a.save()

            for src in work_b.worksource_set.all():
                src.media = work_a
                src.save()

            for item in work_b.poolitem_set.all():
                item.work = work_a
                item.save()

            for relation in work_b.relation_A.all():
                if relation.B.id == work_a.id:
                    relation.delete()
                else:
                    relation.A = work_a
                    relation.save()

            for relation in work_b.relation_B.all():
                if relation.A.id == work_a.id:
                    relation.delete()
                else:
                    relation.B = work_a
                    relation.save()

            work_b.moved_to = work_a
            work_b.save()

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

def relations(request: HttpRequest, work_id: int):
    work = get_work_by_id(work_id)
    relations, works = WorkRelation.get_component_from_work(work)
    return render(request, 'works/relations.html', { 'work': work, 'relations': relations, 'works': works })
