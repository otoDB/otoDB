from itertools import repeat

from django.http import HttpRequest

from ninja import Router
from ninja.security import django_auth

from django.db import transaction
from django.shortcuts import get_object_or_404

from otodb.models import TagWork, SourceWork, MediaWork, UserRequest, BulkRequest, TagWorkParenthood
from otodb.models.enums import RequestActions

def validate(model, field):
    return lambda value: model.objects.get(**{ field: value })

TAGWORK_SLUG_VALIDATOR = validate(TagWork, 'slug')
MEDIAWORK_ID_VALIDATOR = validate(MediaWork, 'id')
SOURCEWORK_ID_VALIDATOR = validate(SourceWork, 'id')

# Numbers to be replaced by an enum
COMMANDS = {
    'worktag:alias':        (RequestActions.TAGWORK_ALIAS,          TAGWORK_SLUG_VALIDATOR,     repeat(TAGWORK_SLUG_VALIDATOR)),
    'worktag:unalias':      (RequestActions.TAGWORK_UNALIAS,        TAGWORK_SLUG_VALIDATOR,     ()),
    'worktag:deprecate':    (RequestActions.TAGWORK_DEPRECATE,      TAGWORK_SLUG_VALIDATOR,     ()),
    'worktag:undeprecate':  (RequestActions.TAGWORK_UNDEPRECATE,    TAGWORK_SLUG_VALIDATOR,     ()),
    'worktag:parent':       (RequestActions.TAGWORK_PARENT,         TAGWORK_SLUG_VALIDATOR,     repeat(TAGWORK_SLUG_VALIDATOR)),
    'worktag:unparent':     (RequestActions.TAGWORK_UNPARENT,       TAGWORK_SLUG_VALIDATOR,     repeat(TAGWORK_SLUG_VALIDATOR)),

    'source:attach-tag':    (RequestActions.WORKSOURCE_ATTACHTAG,   SOURCEWORK_ID_VALIDATOR,    repeat(TAGWORK_SLUG_VALIDATOR)),
    'work:attach-tag':      (RequestActions.MEDIAWORK_ATTACHTAG,    MEDIAWORK_ID_VALIDATOR,     repeat(TAGWORK_SLUG_VALIDATOR)),
}

ACTIONS = {
    RequestActions.TAGWORK_ALIAS:           lambda A, B: TagWork.alias([B], A),
    RequestActions.TAGWORK_UNALIAS:         lambda A, B: TagWork.objects.filter(id=A.id).update(aliased_to=None),
    RequestActions.TAGWORK_DEPRECATE:       lambda A, B: TagWork.objects.filter(id=A.id).update(deprecated=True),
    RequestActions.TAGWORK_UNDEPRECATE:     lambda A, B: TagWork.objects.filter(id=A.id).update(deprecated=False),
    RequestActions.TAGWORK_PARENT:          lambda A, B: TagWorkParenthood.objects.create(tag=A, parent=B).update(deprecated=False),
    RequestActions.TAGWORK_UNPARENT:        lambda A, B: TagWorkParenthood.objects.create(tag=A, parent=B).delete(),

    RequestActions.WORKSOURCE_ATTACHTAG:    lambda A, B: ...,
    RequestActions.MEDIAWORK_ATTACHTAG:     lambda A, B: A.tags.add(B),
}

request_router = Router()

@request_router.post('new', auth=django_auth)
@transaction.atomic
def make_bulk(request: HttpRequest, s: str):
    lines = [line for line in s.splitlines() if line.strip()]
    c = lines.split()
    cmd, A_validator, Bs_validator, _ = COMMANDS[c[0]]
    A = A_validator(c[1])
    bulk = BulkRequest.objects.create(request.user)
    for arg, v in zip(c[2:], Bs_validator):
        UserRequest.objects.create(bulk=bulk, command=cmd, A=A, B=v(arg))

@request_router.post('confirm', auth=django_auth)
@transaction.atomic
def confirm(request: HttpRequest, request_id: int):
    bulk = get_object_or_404(BulkRequest, id=request_id)
    for r in bulk.request_set:
        ACTIONS[r.command](r.A, r.B)
