from django.urls import path

from . import views
from .models import TagWork

app_name = "otodb"
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("query/<str:query_type>", views.query, name="query"),

    path("works/new", views.works.new, name="work_new"),
    path("works/<int:work_id>", views.works.work, name="work"),
    path("works/<int:work_id>/edit", views.works.edit, name="work_edit"),
    path("works/<int:work_id>/new_source", views.works.new_source, name="work_new_source"),
    path("works/<int:work_id>/set_tags", views.works.set_tags, name="work_set_tags"),

    path("lists/new", views.lists.new, name="list_new"),
    path("lists/<int:list_id>", views.lists.list, name="list"),
    path("lists/<int:list_id>/edit", views.lists.edit, name="list_edit"),
    path("lists/<int:list_id>/delete", views.lists.delete, name="list_delete"),

    path("tag/<int:tag_id>", views.tags.tag, name="tag"),
    path("tag/alias", views.tags.alias, name="tag_alias"),

    path("profile/<int:user_id>", views.users.profile, name="profile"),
    path("profile/<int:user_id>/lists", views.users.lists, name="profile_lists"),

    path("login", views.users.login_view, name="login"),
    path("register", views.users.register_view, name="register"),
    path("logout", views.users.logout_view, name="logout"),
]
