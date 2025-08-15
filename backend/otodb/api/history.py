from typing import Literal
from itertools import pairwise

from datetime import datetime

import diff_match_patch as dmp_mod

from django.db.models import Value
from django.forms.models import model_to_dict
from django.http import HttpRequest

from ninja import Router, Schema
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import MediaWork, MediaSong, TagWork, TagSong, WikiPage
from otodb.account.models import Account

from .common import user_is_editor

history_router = Router()

model_classes_with_history = {
    'mediawork': MediaWork,
    'mediasong': MediaSong,
    'tagwork': TagWork,
    'tagsong': TagSong,
    'wikipage': WikiPage
}
models_with_history = model_classes_with_history.keys()

class SmallHistorySchema(Schema):
    history_id: int
    history_date: datetime
    history_user__username: str
    model: str

history_querysets = [c.history.order_by().annotate(
        model=Value(c._meta.model_name),
    ).values(*SmallHistorySchema.model_fields.keys()) for c in model_classes_with_history.values()]

combined_history_queryset = history_querysets[0].union(*history_querysets[1:])

dmp = dmp_mod.diff_match_patch()
def get_diff(delta):
    def diff_prettyHtml(diffs):
        html = []
        for (op, data) in diffs:
            text = (data.replace("&", "&amp;").replace("<", "&lt;")
                        .replace(">", "&gt;").replace("\n", "&para;<br>"))
            if op == dmp.DIFF_INSERT:
                html.append("<ins>%s</ins>" % text)
            elif op == dmp.DIFF_DELETE:
                html.append("<del>%s</del>" % text)
            elif op == dmp.DIFF_EQUAL:
                html.append("<span>%s</span>" % text)
        return "".join(html)

    diffs_html = []

    for change in delta.changes:
        # match change.field:
        #     case 'tags':
        #         # TODO make this not hardcoded...
        #         old, new = set([c['work_tag'] for c in change.old]), set([c['work_tag'] for c in change.new])
        #         old, new = old - new, new - old
        #         changes = ['- ' + TagWork.objects.get(id=id_).slug for id_ in old] + ['+ ' + TagWork.objects.get(id=id_).slug for id_ in new]
        #         diffs_html.append({'html': ('<br>').join(changes), 'field': change.field})
        #     case _:
        old, new = change.old, change.new
        diff_field = dmp.diff_main(str(old), str(new))
        dmp.diff_cleanupSemantic(diff_field)

        diffs_html.append({'html': diff_prettyHtml(diff_field).replace('&para;', ''), 'field': change.field})

    return diffs_html

class DeltaSchema(Schema):
    html: str
    field: str

class HistorySchema(Schema):
    history_id: int
    history_date: datetime
    history_user: str
    history_change_reason: str | None
    delta: list[DeltaSchema]

def get_history_dict(historical):
    d = model_to_dict(historical, fields=[
        'history_id',
        'history_date',
        'history_user',
        'history_change_reason'
    ]) | {'delta': []}
    d['history_user'] = Account.objects.get(id=d['history_user']).username
    return d

@history_router.get('history',
    response=list[HistorySchema]
)
@paginate(pass_parameter='pagination_info')
def history(request: HttpRequest, pk: int, model: Literal[*models_with_history], **kwargs):
    historicals = model_classes_with_history[model].objects.get(id=pk).history.order_by('-history_date')[:kwargs['pagination_info'].limit + 1]
    assert(historicals)

    results = []
    for a, b in pairwise(historicals):
        delta = a.diff_against(b)
        d = get_history_dict(a)
        d['delta'] = get_diff(delta)
        results.append(d)
    results.append(get_history_dict(historicals[-1]))

    return results

@history_router.get('user', response=list[SmallHistorySchema])
@paginate
def recent(request: HttpRequest):
    return combined_history_queryset.order_by('-history_date')

@history_router.get('user', response=list[SmallHistorySchema], auth=django_auth)
@paginate
def user(request: HttpRequest, username: str):
    return combined_history_queryset.filter(history_user=request.user).order_by('-history_date')

@history_router.post('rollback', auth=django_auth)
@user_is_editor
def rollback(request: HttpRequest, model: Literal[*models_with_history], history_id: int):
    model_classes_with_history[model].history.get(history_id=history_id).instance.save()
