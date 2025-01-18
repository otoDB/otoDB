from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from otodb.common import playlist_info
from otodb.models import Pool, PoolItem


class ListForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ['name', 'description']

class ListImportForm(forms.Form):
    link = forms.CharField(label='Link', required=True)

def list(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    works = list_.poolitem_set.select_related('work').order_by('order')
    return render(request, "lists/list.html", {"list": list_, 'works': works})

@login_required
def new(request: HttpRequest):
    if request.method == 'POST':
        form = ListForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['description']

            list_ = Pool(name=name, description=desc, author=request.user)
            list_.save()

            return redirect('otodb:list_edit', list_id=list_.id)

    else:
        form = ListForm()

    return render(request, 'lists/new.html', {'form': form})

@login_required
def edit(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    if list_.author != request.user:
        return redirect('otodb:list', list_id=list_.id)

    error = None
    if request.method == 'POST':
        list_form = ListForm(request.POST, instance=list_)
        if list_form.has_changed() and list_form.is_valid():
            name = list_form.cleaned_data['name']
            desc = list_form.cleaned_data['description']
            list_.name = name
            list_.description = desc
            list_.save()
        try:
            sz = int(request.POST['size'])
            new_entries = [(i, int(request.POST[f'work-{i}']), request.POST[f'desc-{i}']) for i in range(sz)]
            old_entries = list_.poolitem_set.all()

            # this may fail, so we do this first
            new_entries = [PoolItem(work_id=wk, description=desc, order=i, pool=list_) for (i, wk, desc) in new_entries]

            # old must go first, querysets are lazy
            for old in old_entries: old.delete()
            for new in new_entries: new.save()

            return redirect('otodb:list', list_id=list_.id)
        except Exception as e:
            error = str(e)
    else:
        list_form = ListForm(instance=list_)

    return render(request, "lists/edit.html", {"list": list_, 'error': error, 'list_form': list_form})

@login_required
def delete(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    if list_.author != request.user:
        return redirect('otodb:list', list_id=list_.id)

    list_.delete()

    return redirect("otodb:profile_lists", user_id=request.user.id)

@login_required
def toggle(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    if list_.author != request.user:
        return redirect('otodb:list', list_id=list_.id)

    if request.method == 'POST':
        work_id = request.POST['work_id']
        if entries := list_.work_in_pool(work_id):
            for entry in entries:
                entry.delete()
        else:
            list_.add_work(work_id)
        return HttpResponse('')


    return redirect("otodb:profile_lists", user_id=request.user.id)

from otodb.common import video_info
def video_info_wrapped(uu):
    try:
        return video_info(uu)
    except:
        return {}

@login_required
def list_import(request: HttpRequest):
    if request.method == 'POST':
        form = ListImportForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['link']

            info = playlist_info(url)
            list_ = Pool(name=info['title'], description=info['description'], author=request.user)
            list_.save()
            # TODO temp until we decide on access control schemes
            import multiprocessing
            
            # Querying video infos is done in batches to avoid creating 114514 processes
            batch_size_max = 20
            infos = []
            while len(info['entries']):
                batch_size = min(batch_size_max, len(info['entries']))
                pool = multiprocessing.Pool(processes=batch_size)
                batch = info['entries'][:batch_size]
                del info['entries'][:batch_size]
                print(f'{len(info['entries'])} videos remaining')
                infos += pool.map(video_info_wrapped, batch)

            for i, vid_info in enumerate(infos):
                if vid_info == {}: continue
                from otodb.models import WorkSource, MediaWork
                from otodb.models.enums import WorkOrigin
                from datetime import date
                from .works import check_source_duplicates, add_tags_to_work
                src = check_source_duplicates(vid_info)
                work = None
                if not src: # src does not exist
                    work = MediaWork(title=vid_info['title'], description=vid_info['description'], thumbnail=vid_info['thumb'])
                    src = WorkSource(media=work, title=vid_info['title'], description=vid_info['description'],
                        url=vid_info['url'], platform=vid_info['site'], source_id=vid_info['id'],
                        published_date=date.fromtimestamp(vid_info['timestamp']),
                        work_origin=WorkOrigin(False), thumbnail=vid_info.get('thumb', None),
                        work_width=vid_info.get('work_width',None), work_height=vid_info.get('work_height',None))
                    work.save()
                    add_tags_to_work(work, vid_info)
                    src.save()
                else:
                    work = src.media

                PoolItem(work=work, description='', order=i, pool=list_).save()

            return redirect('otodb:list_edit', list_id=list_.id)

    else:
        form = ListImportForm()

    return render(request, 'lists/import.html', {'form': form})
