from typing import Literal
from itertools import pairwise
from functools import wraps

from datetime import datetime

import diff_match_patch as dmp_mod

from django.db.models import Value, F
from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from ninja import Router, Schema, Field
from ninja.pagination import paginate
from ninja.security import django_auth

from otodb.models import TagWork
from otodb.account.models import Account

from .common import user_is_staff, ThinWorkSchema, SongSchema, TagWorkSchema, TagSongSchema

history_router = Router()

def union_qs(qss, **kwargs):
    if len(qss) > 1:
        return qss[0].union(*qss[1:], **kwargs)
    else:
        return qss[0]

model_classes_with_history = {
    'mediawork': [('mediawork', 'id'), ('workrelation', 'A__id'), ('workrelation', 'B__id'), ('worksource', 'media__id')],
    'mediasong': [('mediasong', 'id'), ('songrelation', 'A__id'), ('songrelation', 'B__id'), ('mediasongconnection', 'song__id')],
    'tagwork': [('tagwork', 'id'), ('wikipage', 'tag__id'), ('tagworkconnection', 'tag__id'), ('tagworkmediaconnection', 'tag__id'), ('tagworkcreatorconnection', 'tag__id'), ('tagworklangpreference', 'tag__id')],
    'tagsong': [('tagsong', 'id')],
}
models_with_history = model_classes_with_history.keys()
model_classes_reverse = {cc[0]: k for k, c in model_classes_with_history.items() for cc in c}

class HistoryExtSchema(Schema):
    id: int = Field(..., alias='history_id')
    date: datetime = Field(..., alias='history_date')
    user: str = Field(..., alias='history_user__username')
    model: str
    instance: SongSchema | ThinWorkSchema | TagWorkSchema | TagSongSchema

def get_history_querysets(**kwargs):
    return {model: union_qs([ContentType.objects.get(model=c).model_class().history.order_by().filter(history_user__isnull=False, **kwargs).annotate(
        model=Value(c),
        instance=F(key)
    ).values('history_id', 'history_date', 'history_user__username', 'model', 'instance') for c, key in cc], all=True) for model, cc in model_classes_with_history.items()}

def get_instance_history_querysets(pk):
    return {model: [ContentType.objects.get(model=c).model_class().history.order_by().filter(history_user__isnull=False, **{key: pk}).annotate(
        model=Value(c),
    ) for c, key in cc] for model, cc in model_classes_with_history.items()}

def get_combined_history_queryset(**kwargs):
    return union_qs(list(get_history_querysets(**kwargs).values()), all=True)

def resolve_history_instance_id(f):
    @wraps(f)
    def act(*args, **kwargs):
        qs = f(*args, **kwargs)
        qqs = []
        for q in qs['items']:
            instance_target_model = ContentType.objects.get(model=model_classes_reverse[q['model']]).model_class()
            try:
                q['instance'] = instance_target_model.objects.get(id=q['instance'])
                qqs.append(q)
            except instance_target_model.DoesNotExist:
                pass
        return { 'items': qqs, 'count': qs['count'] }
    return act

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
    id: int = Field(..., alias='history_id')
    date: datetime = Field(..., alias='history_date')
    user: str = Field(..., alias='history_user')
    reason: str | None = Field(..., alias='history_change_reason')
    delta: list[DeltaSchema]

def get_history_dict(historical):
    d = model_to_dict(historical, fields=[
        'history_id',
        'history_date',
        'history_user',
        'history_change_reason'
    ]) | {'delta': []}
    if d['history_user']:
        d['history_user'] = Account.objects.get(id=d['history_user']).username
    else:
        d['history_user'] = Account.objects.get(id=1).username
    return d

@history_router.get('history', response=list[HistorySchema])
@paginate(pass_parameter='pagination_info')
def history(request: HttpRequest, pk: int | str, model: Literal[*models_with_history], **kwargs):
    if model == 'tagwork' or model == 'tagsong':
        pk = get_object_or_404(ContentType.objects.get(model=model).model_class().objects, slug=pk).pk
    historicals = [list(qs.order_by('-history_date')[:kwargs['pagination_info'].limit]) for qs in get_instance_history_querysets(pk)[model]]
    assert(historicals)

    results = []
    for model in historicals:
        for a in model:
            b = a.prev_record
            d = get_history_dict(a)
            if b:
                delta = a.diff_against(b)
                d['delta'] = get_diff(delta)
            else:
                d['delta'] = [{'html': 'created', 'field': a.model }]
            results.append(d)
    results.sort(key=lambda x: x['history_date'], reverse=True)

    return results

@history_router.get('recent', response=list[HistoryExtSchema])
@resolve_history_instance_id
@paginate
def recent(request: HttpRequest):
    return get_combined_history_queryset().order_by('-history_date')

@history_router.get('user', response=list[HistoryExtSchema])
@resolve_history_instance_id
@paginate
def user(request: HttpRequest, username: str):
    return get_combined_history_queryset(history_user__username=username).order_by('-history_date')

@history_router.post('rollback', auth=django_auth)
@user_is_staff # for now
def rollback(request: HttpRequest, model: Literal[*models_with_history], history_id: int):
    model_classes_with_history[model].history.get(history_id=history_id).instance.save()
