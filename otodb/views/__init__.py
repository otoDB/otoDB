from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import *

from otodb.models import MediaSong, MediaWork, TagMain

from . import works, tags, lists, users

def index(request: HttpRequest):
    return render(request, "index.html", {
        "random_work": MediaWork.objects.random()
        }
    )

SEARCH_TYPE_LOOKUP = {
    "work": lambda q: MediaWork.objects.filter(title__contains=q),
    "song": lambda q: MediaSong.objects.filter(title__contains=q),
    "tag":  lambda q:TagMain.objects.filter(name__contains=q),
    "wiki": None
}
def search(request: HttpRequest):
    search_type = request.GET.get('type')
    query = request.GET.get('query')
    results = SEARCH_TYPE_LOOKUP[search_type](query)
    return render(request, "search.html", {"results": results, "type": search_type, 'query': query})
