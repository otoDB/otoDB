from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *

from otodb.models import MediaSong, MediaWork, WorkSource, TagMain

def tag(request: HttpRequest, tag_id: int):
    tag = get_object_or_404(TagMain, pk=tag_id)
    aliases = TagMain.objects.filter(aliased_to=tag)
    works = MediaWork.objects.filter(tags__id=tag_id)
    return render(request, "tags/tag.html", {"tag": tag, "works": works, 'aliases': aliases})

@login_required
def alias(request: HttpRequest):
    redir = 1
    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            into = int(request.POST['into'])
            tags = [TagMain.objects.get(name=request.POST[f'tag-{i}']) for i in range(n)]
            into = tags[into]
            redir = into.id

            for tag in tags:
                if tag is not into:
                    tag.aliased_to = into
                    tag.save()
                    # todo drop all tags tag, join into into
        except Exception as e:
            print(e)

    return redirect('otodb:tag', tag_id=into.id)
