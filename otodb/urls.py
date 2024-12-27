from django.urls import path

from . import views

app_name = "otodb"
urlpatterns = [
    path("", views.index, name="index"),

    path("new_work", views.new_work, name="new_work"),
    path("work/<int:work_id>", views.work, name="work"),
    path("work/<int:work_id>/edit", views.edit_work, name="edit_work"),
    path("work/<int:work_id>/new_source", views.new_source, name="new_source"),
    path("work/<int:work_id>/attach_tag", views.attach_tag, name="attach_tag"),

    path("new_list", views.new_list, name="new_list"),
    path("list/<int:list_id>", views.list, name="list"),
    path("list/<int:list_id>/edit", views.list_edit, name="list_edit"),
    path("list/<int:list_id>/delete", views.list_delete, name="list_delete"),

    path("tag/<int:tag_id>", views.tag, name="tag"),

    path("search", views.search, name="search"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("profile/<int:user_id>/lists", views.user_lists, name="user_lists"),

    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
]
