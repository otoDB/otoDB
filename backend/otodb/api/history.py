from typing import Literal
from itertools import pairwise

from datetime import datetime

import diff_match_patch as dmp_mod

from django.db.models import Value, F
from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router, Schema
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import MediaWork, MediaSong, TagWork, TagSong, WikiPage
from otodb.account.models import Account

from .common import user_is_editor, ThinWorkSchema, SongSchema, TagWorkSchema, TagSongSchema

history_router = Router()

model_classes_with_history = {
    'mediawork': MediaWork,
    'mediasong': MediaSong,
    'tagwork': TagWork,
    'tagsong': TagSong,
    'wikipage': WikiPage
}
models_with_history = model_classes_with_history.keys()

class HistoryExtSchema(Schema):
    history_id: int
    history_date: datetime
    history_user__username: str
    model: str
    instance: ThinWorkSchema | SongSchema | TagWorkSchema | TagSongSchema

def get_history_querysets(**kwargs):
    return [c.history.order_by().filter(**kwargs).annotate(
        model=Value(c._meta.model_name),
        instance=F('id')
    ).values(*HistoryExtSchema.model_fields.keys()) for c in model_classes_with_history.values()]

def get_combined_history_queryset(**kwargs):
    qs = get_history_querysets(**kwargs)
    return qs[0].union(*qs[1:])

def resolve_instance_id(qs):
    qqs = []
    for q in qs:
        try:
            q['instance'] = model_classes_with_history[q['model']].objects.get(id=q['instance'])
            if q['model'] == 'wikipage':
                q['instance'] = q['instance'].tag
            qqs.append(q)
        except model_classes_with_history[q['model']].DoesNotExist:
            pass            
    return qqs

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
        if 'tag' in change.field:
            field = [f for f in (change.old + change.new)[0].keys() if 'tag' in f][0]
            old, new = {c[field] for c in change.old}, {c[field] for c in change.new}
            old, new = old - new, new - old
            changes = ['- ' + t for t in TagWork.objects.filter(id__in=old).values_list('slug', flat=True)] + ['+ ' + t for t in TagWork.objects.filter(id__in=new).values_list('slug',flat=True)]
            diffs_html.append({'html': ('<br>').join(changes), 'field': change.field})
        else:
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
def history(request: HttpRequest, pk: int | str, model: Literal[*models_with_history], **kwargs):
    if model == 'tagwork':
        obj = get_object_or_404(model_classes_with_history[model], slug=pk)
    else:
        obj = get_object_or_404(model_classes_with_history[model], id=pk)
    historicals = obj.history.order_by('-history_date')[:kwargs['pagination_info'].limit + 1]
    historicals = [*historicals]
    assert(historicals)

    results = []
    for a, b in pairwise(historicals):
        delta = a.diff_against(b)
        d = get_history_dict(a)
        d['delta'] = get_diff(delta)
        results.append(d)
    results.append(get_history_dict(historicals[-1]))

    return results

@history_router.get('recent', response=list[HistoryExtSchema])
@paginate
def recent(request: HttpRequest):
    return resolve_instance_id(get_combined_history_queryset.order_by('-history_date'))

@history_router.get('user', response=list[HistoryExtSchema], auth=django_auth)
@paginate
def user(request: HttpRequest, username: str):
    return resolve_instance_id(get_combined_history_queryset(history_user=request.user).order_by('-history_date'))

@history_router.post('rollback', auth=django_auth)
@user_is_editor
def rollback(request: HttpRequest, model: Literal[*models_with_history], history_id: int):
    model_classes_with_history[model].history.get(history_id=history_id).instance.save()
