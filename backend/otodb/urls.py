from django.urls import path

from . import views
from .api import api

app_name = "otodb"
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("query/<str:query_type>", views.query, name="query"),

    path("api/", api.urls),

    path("works/new", views.works.new, name="work_new"),
    path("works/merge", views.works.merge, name="work_merge"),
    path("works/<int:work_id>", views.works.work, name="work"),
    path("works/<int:work_id>/edit", views.works.edit, name="work_edit"),
    path("works/<int:work_id>/set_tags", views.works.set_tags, name="work_set_tags"),
    path("works/<int:work_id>/history", views.works.history, name="work_history"),
    path("works/<int:work_id>/relations", views.works.relations, name="work_relations"),
    path("works/<int:work_id>/edit_relations", views.works.edit_relations, name="work_edit_relations"),
    path("works/checkin/<int:source_id>", views.works.check_in_source, name="work_check_in_source"),

    path("work_tags/alias", views.tags.work_alias, name="tag_alias"),
    path("work_tags/<str:tag_slug>", views.tags.work_tag, name="tag"),
    path("work_tags/<str:tag_slug>/edit", views.tags.work_edit, name="tag_edit"),
    path("work_tags/<str:tag_slug>/history", views.tags.work_history, name="tag_history"),
    path("work_tags/<str:tag_slug>/wiki_page", views.tags.wiki_page, name="tag_wiki_page"),
    path("work_tags/<str:tag_slug>/new_wiki_page", views.tags.new_wiki_page, name="tag_new_wiki_page"),
    path("work_tags/<str:tag_slug>/edit_wiki_page", views.tags.edit_wiki_page, name="tag_edit_wiki_page"),

    path("source/<int:source_id>/refresh", views.works.refresh_source, name="source_refresh"),

    path("songs/<int:song_id>", views.songs.song, name="song"),
    path("songs/<int:song_id>/edit", views.songs.edit, name="song_edit"),
    path("songs/<int:song_id>/history", views.songs.history, name="song_history"),
    path("songs/<int:song_id>/relations", views.songs.relations, name="song_relations"),
    path("songs/<int:song_id>/edit_relations", views.songs.edit_relations, name="song_edit_relations"),
    path("songs/new_from_tag/<str:tag_slug>", views.songs.new_from_tag, name="song_new_from_tag"),

    # path("song_tags/alias", views.tags.song_alias, name="song_tag_alias"),
    # path("song_tags/<int:tag_id>", views.tags.song_tag, name="song_tag"),
    # path("song_tags/<int:tag_id>/history", views.tags.song_history, name="song_tag_history"),

    path("lists/new", views.lists.new, name="list_new"),
    path("lists/import", views.lists.list_import, name="list_import"),
    path("lists/<int:list_id>", views.lists.list, name="list"),
    path("lists/<int:list_id>/edit", views.lists.edit, name="list_edit"),
    path("lists/<int:list_id>/delete", views.lists.delete, name="list_delete"),
    path("lists/<int:list_id>/toggle", views.lists.toggle, name="list_toggle"),

    path("profile/<int:user_id>", views.users.profile, name="profile"),
    path("profile/<int:user_id>/lists", views.users.lists, name="profile_lists"),

    path("login", views.users.login_view, name="login"),
    path("register", views.users.register_view, name="register"),
    path("logout", views.users.logout_view, name="logout"),

    path("upload_youtube_cookies", views.upload_youtube_cookies, name="upload_youtube_cookies"),
]
