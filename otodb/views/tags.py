from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from otodb.models import MediaWork, TagWork

def tag(request: HttpRequest, tag_id: int):
    tag = get_object_or_404(TagWork, pk=tag_id)
    works = MediaWork.objects.filter(tags__id=tag_id)
    return render(request, "tags/tag.html", {"tag": tag, "works": works})

@login_required
def alias(request: HttpRequest):
    # alias tree is at most one layer deep
    if request.method == 'POST':
        try:
            n = int(request.POST['size'])
            into = int(request.POST['into'])
            tags = [TagWork.objects.get(name=request.POST[f'tag-{i}']) for i in range(n)]
            into = tags[into]
            if into.aliased_to:
                into = into.aliased_to

            for tag in tags:
                if tag is not into:
                    tag.aliased_to = into
                    tag.save()
                    for work in MediaWork.objects.filter(tags__id=tag.id):
                        work.tags.add(into)
                        work.tags.remove(tag)
                    for t in TagWork.objects.filter(aliased_to=tag):
                        t.aliased_to = into

            return redirect('otodb:tag', tag_id=into.id)        
        except Exception as e:
            print(e)

    return render(request, 'tags/alias.html')
