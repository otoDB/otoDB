from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, Http404
from django.shortcuts import get_object_or_404, redirect, render

from simple_history.utils import update_change_reason

from otodb.models import MediaSong, TagWork, TagSong, SongRelation
from otodb.models.enums import WorkTagCategory, SongRelationTypes

class SongForm(forms.ModelForm):
    class Meta:
        model = MediaSong
        fields = ['title', 'bpm', 'author']
    
class SongEditForm(SongForm):
    reason = forms.CharField(label="Update Reason", required=True)

@login_required
def new_from_tag(request: HttpRequest, tag_slug: str):
    tag = get_object_or_404(TagWork, slug=tag_slug)
    if tag.aliased_to is not None:
        tag = tag.aliased_to
    if tag.category == WorkTagCategory.SONG:
        raise Http404("This tag is already a song tag.")

    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            form.instance.work_tag = tag
            form.save()
            tag.category = WorkTagCategory.SONG
            tag.save()
            return redirect('otodb:tag', tag_slug=tag_slug)

    else:
        form = SongForm()
        
    return render(request, 'songs/new_from_tag.html', { 'form': form, 'tag': tag })

def song(request: HttpRequest, song_id: int):
    song = get_object_or_404(MediaSong, id=song_id)
    return redirect('otodb:tag', song.work_tag.slug)

def history(request: HttpRequest, song_id: int):
    song = get_object_or_404(MediaSong, pk=song_id)
    
    history = []
    for record in song.history.all().reverse():
        if history != []:
            prev = history[-1]
            delta = record.diff_against(prev)
            record.history_delta_changes = get_diff(delta)
        history.append(record)
    history.reverse()
    return render(request, 'songs/history.html', { 'song': song, 'history': history })

def relations(request: HttpRequest, song_id: int):
    song = get_object_or_404(MediaSong, id=song_id)
    relations, songs = SongRelation.get_component_from_song(song)
    return render(request, 'songs/relations.html', { 'song': song, 'relations': relations, 'songs': songs })

@login_required
def edit_relations(request: HttpRequest, song_id: int):
    song = get_object_or_404(MediaSong, id=song_id)

    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            new_relations = [(int(request.POST[f'relation-{i}']), int(request.POST[f'song-{i}']), bool(int(request.POST[f'direction-{i}']))) for i in range(n)]
            new_relations = [SongRelation(B_id=song_id, A_id=w, relation=r) if d else SongRelation(A_id=song_id, B_id=w, relation=r) for r, w, d in new_relations]
            
            old_relations = SongRelation.get_relations_including_songs([song])
            for r in old_relations:
                r.delete()
            for r in new_relations:
                r.save()

        except Exception as e:
            print(e)

    return redirect('otodb:song_relations', song_id=song.id)

@login_required
def edit(request: HttpRequest, song_id: int):
    song = get_object_or_404(MediaSong, id=song_id)
    relations = SongRelation.get_relations_including_songs([song])

    if request.method == 'POST':
        form = SongEditForm(request.POST, instance=song)

        if form.has_changed() and form.is_valid():
            form.save()
            update_change_reason(song, form.cleaned_data['reason'])
            return redirect('otodb:song', song_id=song.id)

    else:
        form = SongEditForm(instance=song)

    return render(request, 'songs/edit.html', { 'song': song, 'form': form, 'relations': relations, 'relation_types': SongRelationTypes })

