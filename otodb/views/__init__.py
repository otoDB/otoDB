from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from otodb.models import MediaSong, MediaWork, Pool, TagWork

from . import lists, tags, users, works, songs

__all__ = ['lists', 'tags', 'users', 'works', 'songs']


def index(request: HttpRequest):
    return render(request, "index.html", {
        "random_work": MediaWork.objects.random()
        }
    )

SEARCH_TYPE_LOOKUP = {
    "work": lambda q: MediaWork.objects.filter(title__contains=q, moved_to__isnull=True),
    "song": lambda q: MediaSong.objects.filter(title__contains=q),
    "tag":  lambda q: TagWork.objects.filter(name__contains=q, aliased_to__isnull=True)
}
def search(request: HttpRequest):
    if request.method == 'GET':
        search_type = request.GET.get('type')
        query = request.GET.get('query')
        results = SEARCH_TYPE_LOOKUP[search_type](query)
        paginator = Paginator(results, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(request, "search.html", {"results": page_obj, "type": search_type, 'query': query})
    else:
        return redirect('otodb:index')

@login_required
def query(request: HttpRequest, query_type: str):
    if request.method == 'GET':
        q = request.GET.get('query')
        if q != '': # reject empty query
            results = None
            match query_type:
                case 'work':
                    results = MediaWork.objects.filter(title__contains=q, moved_to__isnull=True)
                    return render(request, "query/works.html", {'results': results})
                case 'tag':
                    results = TagWork.objects.filter(name__contains=q, aliased_to__isnull=True)
                    return render(request, "query/tags.html", {'results': results})
                case 'list':
                    results = request.user.pool_set
                    work_id = request.GET['work_id']
                    results = [(lst, lst.work_in_pool(work_id).exists()) for lst in results.all()]
                    return render(request, "query/lists.html", {'results': results, 'work_id': work_id})
                case 'song':
                    results = MediaSong.objects.filter(title__contains=q)
                    return render(request, "query/songs.html", {'results': results})
    return HttpResponse('')

