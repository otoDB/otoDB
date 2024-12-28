from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect, render

from otodb.models import MediaSong, MediaWork, Pool, TagWork

from . import lists, tags, users, works

__all__ = ['lists', 'tags', 'users', 'works']


def index(request: HttpRequest):
    return render(request, "index.html", {
        "random_work": MediaWork.objects.random()
        }
    )

SEARCH_TYPE_LOOKUP = {
    "work": lambda q: MediaWork.objects.filter(title__contains=q),
    "song": lambda q: MediaSong.objects.filter(title__contains=q),
    "tag":  lambda q: TagWork.objects.filter(name__contains=q),
    "wiki": None
}
def search(request: HttpRequest):
    search_type = request.GET.get('type')
    query = request.GET.get('query')
    results = SEARCH_TYPE_LOOKUP[search_type](query)
    return render(request, "search.html", {"results": results, "type": search_type, 'query': query})

@login_required
def query(request: HttpRequest, query_type: str):
    if request.method == 'GET':
        q = request.GET.get('query')
        results = None
        match query_type:
            case 'work':
                results = MediaWork.objects.filter(title__contains=q)
                return render(request, "query/works.html", {'results': results})
            case 'tag':
                results = TagWork.objects.filter(name__contains=q, aliased_to__isnull=True)
                return render(request, "query/tags.html", {'results': results})
            case 'mylists':
                results = Pool.objects.filter(author=request.user)
                return render(request, "query/lists.html", {'results': results})
    return redirect('otodb:index')
