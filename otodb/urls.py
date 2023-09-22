from django.urls import path

from . import views

app_name = "otodb"
urlpatterns = [
    path("", views.index, name="index")
]
