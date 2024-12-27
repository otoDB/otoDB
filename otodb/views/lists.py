from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *
from django import forms

from otodb.models import Pool, PoolItem

class ListForm(forms.ModelForm):
    class Meta:
        model = Pool
        fields = ['name', 'description', 'status']

def list(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    works = PoolItem.objects.filter(pool=l).select_related('work').order_by('order')
    return render(request, "lists/list.html", {"list": l, 'works': works})

@login_required
def new(request: HttpRequest):
    if request.method == 'POST':
        form = ListForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            desc = form.cleaned_data['description']
            stat = form.cleaned_data['status']

            l = Pool(name=name, description=desc, status=stat, author=request.user)
            l.save()

            return redirect('otodb:list_edit', list_id=l.pk)

    else:
        form = ListForm()

    return render(request, 'lists/new.html', {'form': form})

@login_required
def edit(request: HttpRequest, list_id: int):
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

    return render(request, "lists/edit.html", {"list": l, 'error': error, 'list_form': list_form})

@login_required
def delete(request: HttpRequest, list_id: int):
    l = get_object_or_404(Pool, pk=list_id)
    if l.author != request.user:
        return redirect('otodb:list', list_id=l.pk)

    l.delete()

    return redirect("otodb:profile_lists", user_id=request.user.id)
