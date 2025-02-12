from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

from simple_history.utils import update_change_reason

from otodb.common import get_diff
from otodb.models import MediaWork, TagWork, WikiPage
from otodb.models.enums import WorkTagCategory

class WorkTagEditForm(forms.ModelForm):
    reason = forms.CharField(label="Update Reason", required=True)
    class Meta:
        model = TagWork
        fields = ['category', 'parent']

def tag(request: HttpRequest, tag_slug: str, tag_type):
    tag = get_object_or_404(tag_type, slug=tag_slug)
    works = MediaWork.objects.filter(tags__slug=tag_slug, moved_to__isnull=True)
    paginator = Paginator(works, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "tags/tag.html", {"tag": tag, "works": page_obj})

@login_required
def edit(request: HttpRequest, tag_slug: str, tag_type):
    tag = get_object_or_404(tag_type, slug=tag_slug)

    if request.method == 'POST':
        form = WorkTagEditForm(request.POST, instance=tag)
        if form.has_changed() and form.is_valid():
            if tag.category == WorkTagCategory.SONG:
                form.instance.category = WorkTagCategory.SONG # defensive
            form.save()

            update_change_reason(tag, form.cleaned_data['reason'])
            return redirect('otodb:tag', tag_slug=tag.slug)

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

            return redirect('otodb:tag', tag_slug=into.slug)        
        except Exception as e:
            print(e)

    return render(request, 'tags/alias.html')

def history(request: HttpRequest, tag_slug: str, tag_type):
    tag = get_object_or_404(tag_type, slug=tag_slug)

    history = []
    for record in tag.history.all().reverse():
        if history != []:
            prev = history[-1]
            delta = record.diff_against(prev)
            record.history_delta_changes = get_diff(delta)
        history.append(record)
    history.reverse()
    return render(request, 'tags/history.html', { 'tag': tag, 'history': history })

def work_tag(request: HttpRequest, tag_slug: str):
    return tag(request, tag_slug, TagWork)

def work_edit(request: HttpRequest, tag_slug: str):
    return edit(request, tag_slug, TagWork)

def work_alias(request: HttpRequest):
    return alias(request, TagWork)

def work_history(request: HttpRequest, tag_slug: str):
    return history(request, tag_slug, TagWork)

# def song_tag(request: HttpRequest, tag_slug: str):
#     return tag(request, tag_id, TagSong)

# def song_alias(request: HttpRequest):
#     return alias(request, TagSong)

# def song_history(request: HttpRequest, tag_slug: str):
#     return history(request, tag_id, TagSong)

class WikiPageForm(forms.ModelForm):
    # page = forms.CharField(widget=MDEWidget())
    class Meta:
        model = WikiPage
        fields = ['page']

def new_wiki_page(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, pk=tag_slug)
    if tag.wiki_page is not None:
        return redirect('otodb:tag_wiki_page', tag_slug=tag.wiki_page.id)

    if request.method == 'POST':
        form = WikiPageForm(request.POST)
        if form.is_valid():
            page = WikiPage(page=form.cleaned_data['page'])
            page.save()
            tag.wiki_page = page
            tag.save()
            return redirect('otodb:tag_wiki_page', tag_slug=tag.slug)

    else:
        form = WikiPageForm()


    return render(request, 'tags/new_wiki_page.html', { 'tag': tag, 'form': form })


def wiki_page(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, pk=tag_slug)
    if tag.wiki_page is None:
        return redirect('otodb:tag_new_wiki_page', tag_slug=tag.slug)

    return render(request, 'tags/wiki_page.html', { 'tag': tag })


def edit_wiki_page(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, pk=tag_slug)
    if tag.wiki_page is None:
        return redirect('otodb:tag_new_wiki_page', tag_slug=tag.slug)
    if request.method == 'POST':
        form = WikiPageForm(request.POST)
        if form.is_valid():
            page = tag.wiki_page
            page.page = form.cleaned_data['page']
            page.save()
            return redirect('otodb:tag_wiki_page', tag_slug=tag.slug)

    else:
        form = WikiPageForm(instance=tag.wiki_page)


    return render(request, 'tags/edit_wiki_page.html', { 'tag': tag, 'form': form })

