from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from otodb.common import video_info, playlist_info
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
    paginator = Paginator(works, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "lists/list.html", {"list": list_, 'works': page_obj})

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

    works = list_.poolitem_set.select_related('work').order_by('order')
    page_size = 20
    paginator = Paginator(works, page_size)
    page_number = request.GET.get("page") or request.POST.get("page") or 1
    page_obj = paginator.get_page(page_number)

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
            old_entries = page_obj

            # this may fail, so we do this first
            n_previous = (int(page_number) - 1) * page_size
            new_entries = [PoolItem(work_id=wk, description=desc, order=i + n_previous, pool=list_) for (i, wk, desc) in new_entries]
            # old must go first, querysets are lazy
            for entry in old_entries: entry.delete()

            entries_after_page = list_.poolitem_set.filter(order__gte=n_previous)
            for item in entries_after_page:
                item.order += sz - page_size
            PoolItem.objects.bulk_update(entries_after_page, ['order'])
            
            PoolItem.objects.bulk_create(new_entries)

            return redirect('otodb:list', list_id=list_.id)
        except Exception as e:
            error = str(e)
    else:

        list_form = ListForm(instance=list_)

    return render(request, "lists/edit.html", {"list": list_, 'error': error, 'list_form': list_form, 'works': page_obj})

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

def video_info_wrapped(url):
    try:
        return video_info(url)
    except:
        return {'failed': url}

@login_required
def list_import(request: HttpRequest):
    if request.method == 'POST':
        form = ListImportForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['link']

            info = playlist_info(url)
            list_ = Pool(name=info['title'], description=info['description'], author=request.user)

            # IMPORTANT!!!
            # DO NOT TOUCH THIS CODE. BEHAVIOR FROZEN FOR DJANGO FRONTEND
            # INSTEAD MAKE ALL ADJUSTMENTS TO api/list.py:import_ext(...)
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor() as executor:
                infos = executor.map(video_info_wrapped, info['entries'])

            new_works, new_tag_instances, new_sources, pool_items = [], [], [], []
            i = 0
            from otodb.models import WorkSource, MediaWork, TagWork, TagWorkInstance
            from otodb.models.enums import WorkOrigin
            from datetime import date
            for vid_info in infos:
                if 'failed' in vid_info:
                    list_.description += f'\nFailed to fetch {vid_info['failed']}'
                    continue

                src = WorkSource.objects.get(platform=info['site'], source_id=info['id'])
                if not src: # src does not exist
                    work = MediaWork(title=vid_info['title'], description=vid_info['description'], thumbnail=vid_info['thumb'])
                    src = WorkSource(media=work, title=vid_info['title'], description=vid_info['description'],
                        url=vid_info['url'], platform=vid_info['site'], source_id=vid_info['id'],
                        published_date=date.fromtimestamp(vid_info['timestamp']),
                        work_origin=WorkOrigin(False), thumbnail=vid_info.get('thumb', None),
                        work_width=vid_info.get('work_width',None), work_height=vid_info.get('work_height',None))
                    new_works.append(work)
                    new_sources.append(src)
                else:
                    work = src.media

                new_tag_instances.extend([TagWorkInstance(work=work, work_tag=TagWork.objects.get_or_create(name=t)[0]) for t in vid_info['tags']])
                pool_items.append(PoolItem(work=work, description='', order=i, pool=list_))

                i += 1

            list_.save()
            MediaWork.objects.bulk_create(new_works)
            TagWorkInstance.objects.bulk_create(new_tag_instances, ignore_conflicts=True) # bulk_create does not handle M2M so we do this manually
            WorkSource.objects.bulk_create(new_sources)
            PoolItem.objects.bulk_create(pool_items)

            return redirect('otodb:list_edit', list_id=list_.id)

    else:
        form = ListImportForm()

    return render(request, 'lists/import.html', {'form': form})
