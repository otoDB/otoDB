from django.urls import path

from . import views

app_name = "otodb"
urlpatterns = [
    path("", views.index, name="index"),
    path("work/<int:work_id>", views.work, name="work"),
    path("tag/<int:tag_id>", views.tag, name="tag"),
    path("search", views.search, name="search"),
    path("profile", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("new_work", views.new_work, name="new_work"),
]
