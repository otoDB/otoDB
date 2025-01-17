from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from simple_history.utils import update_change_reason

from otodb.common import get_diff
from otodb.models import MediaWork, TagWork
from otodb.models.enums import WorkTagCategory

class WorkTagEditForm(forms.ModelForm):
    reason = forms.CharField(label="Update Reason", required=True)
    class Meta:
        model = TagWork
        fields = ['category', 'parent']

def tag(request: HttpRequest, tag_id: int, tag_type):
    tag = get_object_or_404(tag_type, pk=tag_id)
    works = MediaWork.objects.filter(tags__id=tag_id, moved_to__isnull=True)
    return render(request, "tags/tag.html", {"tag": tag, "works": works})

@login_required
def edit(request: HttpRequest, tag_id:int, tag_type):
    tag = get_object_or_404(tag_type, id=tag_id)

    if request.method == 'POST':
        form = WorkTagEditForm(request.POST, instance=tag)
        if form.has_changed() and form.is_valid():
            if tag.category == WorkTagCategory.SONG:
                form.instance.category = WorkTagCategory.SONG # defensive
            form.save()

            update_change_reason(tag, form.cleaned_data['reason'])
            return redirect('otodb:tag', tag_id=tag.id)

    else:
        form = WorkTagEditForm(instance=tag)
        if tag.category != WorkTagCategory.SONG:
            # exclude song category
            form.fields['category'].choices = form.fields['category'].choices[:2] + form.fields['category'].choices[3:]
        else:
            form.fields['category'].widget = forms.HiddenInput()

    return render(request, 'tags/edit.html', { 'tag': tag, 'form': form })

@login_required
def alias(request: HttpRequest, tag_type):
    # alias tree is at most one layer deep
    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            into = int(request.POST['into'])
            tags = [tag_type.objects.get(name=request.POST[f'tag-{i}']) for i in range(n)]
            into = tags[into]
            if into.aliased_to:
                into = into.aliased_to

            for tag in tags:
                if tag is not into:
                    tag.aliased_to = into
                    tag.save()
                    for work in MediaWork.objects.filter(tags__id=tag.id, moved_to__isnull=True):
                        work.tags.add(into)
                        work.tags.remove(tag)
                    for t in tag_type.objects.filter(aliased_to=tag):
                        t.aliased_to = into
                        t.save()
                    for t in tag_type.objects.filter(parent=tag):
                        t.parent = into
                        t.save()
                    if into.parent is None:
                        into.parent = tag.parent
                    if tag.category == WorkTagCategory.SONG:
                        song = tag.mediasong
                        song.work_tag = into
                        song.save()
                        
            into.save()

            return redirect('otodb:tag', tag_id=into.id)        
        except Exception as e:
            print(e)

    return render(request, 'tags/alias.html')

def history(request: HttpRequest, tag_id: int, tag_type):
    tag = get_object_or_404(tag_type, pk=tag_id)

    history = []
    for record in tag.history.all().reverse():
        if history != []:
            prev = history[-1]
            delta = record.diff_against(prev)
            record.history_delta_changes = get_diff(delta)
        history.append(record)
    history.reverse()
    return render(request, 'tags/history.html', { 'tag': tag, 'history': history })

def work_tag(request: HttpRequest, tag_id: int):
    return tag(request, tag_id, TagWork)

def work_edit(request: HttpRequest, tag_id: int):
    return edit(request, tag_id, TagWork)

def work_alias(request: HttpRequest):
    return alias(request, TagWork)

def work_history(request: HttpRequest, tag_id: int):
    return history(request, tag_id, TagWork)

# def song_tag(request: HttpRequest, tag_id: int):
#     return tag(request, tag_id, TagSong)

# def song_alias(request: HttpRequest):
#     return alias(request, TagSong)

# def song_history(request: HttpRequest, tag_id: int):
#     return history(request, tag_id, TagSong)
