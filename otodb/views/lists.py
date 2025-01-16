from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from otodb.models import Pool, PoolItem


class ListForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ['name', 'description']

class ListImportForm(forms.Form):
    link = forms.CharField(label='Link', required=True)

def list(request: HttpRequest, list_id: int):
    list_ = get_object_or_404(Pool, pk=list_id)
    works = PoolItem.objects.filter(pool=list_).select_related('work').order_by('order')
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
        if list_form.is_valid():
            name = list_form.cleaned_data['name']
            desc = list_form.cleaned_data['description']
            list_.name = name
            list_.description = desc
            list_.save()
        try:
            sz = int(request.POST['size'])
            new_entries = [(i, int(request.POST[f'work-{i}']), request.POST[f'desc-{i}']) for i in range(sz)]
            old_entries = PoolItem.objects.filter(pool=list_)

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


    return redirect("otodb:profile_lists", user_id=request.user.id)

@login_required
def list_import(request: HttpRequest):
    if request.method == 'POST':
        form = ListImportForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['link']

            pass

            # list_ = Pool(name=name, description=desc, author=request.user)
            # list_.save()

            # return redirect('otodb:list_edit', list_id=list_.id)

    else:
        form = ListImportForm()

    return render(request, 'lists/import.html', {'form': form})
