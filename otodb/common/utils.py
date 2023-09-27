from typing import TYPE_CHECKING

import diff_match_patch as dmp_mod
from django.apps import apps

if TYPE_CHECKING:
    from ..models import Implication as T_Implication
    from ..models import MediaSong as T_MediaSong
    from ..models import MediaWork as T_MediaWork
    from ..models.base import MediaBase as T_MediaBase


def space_splitter(tag_string):
    return [t.strip().lower() for t in tag_string.split(' ') if t.strip()]


def space_joiner(tags):
    return ' '.join(t.name for t in tags)


def verify_and_perform_implications(from_tag_name):
    MediaWork: 'T_MediaWork' = apps.get_model('otodb', 'MediaWork')  # type: ignore
    MediaSong: 'T_MediaSong' = apps.get_model('otodb', 'MediaSong')  # type: ignore
    Implication: 'T_Implication' = apps.get_model('otodb', 'Implication')  # type: ignore

    implication = Implication.objects.filter(from_tag__name=from_tag_name, status=1).first()

    if implication is not None:
        from_tag = implication.from_tag
        to_tag = implication.to_tag

        for media_class in [MediaWork, MediaSong]:
            media_class: T_MediaBase
            missing_media = media_class.objects.filter(tags__name__in=[from_tag]).exclude(tags__name__in=[to_tag])

            if missing_media.exists():
                for media in missing_media:
                    media.check_and_update_implications()


def get_diff(field_name, old_revision, new_revision):
    old_revision_field = old_revision.field_dict[field_name]
    new_revision_field = new_revision.field_dict[field_name]

    dmp = dmp_mod.diff_match_patch()
    diff_field = dmp.diff_main(old_revision_field, new_revision_field)
    dmp.diff_cleanupSemantic(diff_field)
    diff_html = dmp.diff_prettyHtml(diff_field).replace('&para;', '')

    return diff_html
