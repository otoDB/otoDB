from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from otodb.models import MediaWork


def index(request: HttpRequest):
    return render(request, "otodb/index.html")

def work(request: HttpRequest, work_id: int):
    return render(request, "otodb/work.html", {"work": MediaWork.objects.get(pk=work_id)})

