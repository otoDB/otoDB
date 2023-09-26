from django.shortcuts import render
from django.http import HttpRequest


def index(request: HttpRequest):
    return render(request, "otodb/index.html")
