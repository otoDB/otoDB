from django.http import HttpRequest
from django.shortcuts import render
from random import choice

from otodb.models import MediaWork


def index(request: HttpRequest):
    rand_work = MediaWork.objects.get(pk=choice(MediaWork.objects.values_list('pk', flat=True)))
    return render(request, "otodb/index.html", {"work": rand_work})

def work(request: HttpRequest, work_id: int):
    return render(request, "otodb/work.html", {"work": MediaWork.objects.get(pk=work_id)})

def search(request: HttpRequest):
    type = request.GET.get('type')
    query = request.GET.get('query')
    results = MediaWork.objects.filter(title__contains=query)
    return render(request, "otodb/search.html", {"results": results})

