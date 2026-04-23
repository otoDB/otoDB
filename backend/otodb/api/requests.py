from itertools import repeat
from typing import Union

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Router, Schema
from ninja.security import django_auth
from pydantic import field_validator

from otodb.models import (
	BulkRequest,
	MediaWork,
	Subscription,
	TagWork,
	TagWorkParenthood,
	UserRequest,
	WorkSource,
)
from otodb.models.enums import RequestActions, Status

from .common import (
	ProfileSchema,
	TagWorkSchema,
	WorkSchema,
	WorkSourceSchema,
	add_revision_message,
	track_revision,
	user_is_editor,
)

ENTITY_SCHEMAS = [TagWorkSchema, WorkSchema, WorkSourceSchema]


def validate(model, field):
	return lambda value: model.objects.get(**{field: value})


TAGWORK_SLUG_VALIDATOR = validate(TagWork, 'slug')
MEDIAWORK_ID_VALIDATOR = validate(MediaWork, 'id')
SOURCEWORK_ID_VALIDATOR = validate(WorkSource, 'id')

# Numbers to be replaced by an enum
COMMANDS = {
	'worktag:alias': (
		RequestActions.TAGWORK_ALIAS,
		TAGWORK_SLUG_VALIDATOR,
		repeat(TAGWORK_SLUG_VALIDATOR),
	),
	'worktag:unalias': (RequestActions.TAGWORK_UNALIAS, TAGWORK_SLUG_VALIDATOR, ()),
	'worktag:deprecate': (RequestActions.TAGWORK_DEPRECATE, TAGWORK_SLUG_VALIDATOR, ()),
	'worktag:undeprecate': (
		RequestActions.TAGWORK_UNDEPRECATE,
		TAGWORK_SLUG_VALIDATOR,
		(),
	),
	'worktag:parent': (
		RequestActions.TAGWORK_PARENT,
		TAGWORK_SLUG_VALIDATOR,
		repeat(TAGWORK_SLUG_VALIDATOR),
	),
	'worktag:unparent': (
		RequestActions.TAGWORK_UNPARENT,
		TAGWORK_SLUG_VALIDATOR,
		repeat(TAGWORK_SLUG_VALIDATOR),
	),
	# 'source:attach-tag': (
	# 	RequestActions.WORKSOURCE_ATTACHTAG,
	# 	SOURCEWORK_ID_VALIDATOR,
	# 	repeat(TAGWORK_SLUG_VALIDATOR),
	# ),
	# 'work:attach-tag': (
	# 	RequestActions.MEDIAWORK_ATTACHTAG,
	# 	MEDIAWORK_ID_VALIDATOR,
	# 	repeat(TAGWORK_SLUG_VALIDATOR),
	# ),
}

ACTIONS = {
	RequestActions.TAGWORK_ALIAS: lambda A, B: TagWork.alias([B], A),
	RequestActions.TAGWORK_UNALIAS: lambda A, B: TagWork.objects.filter(id=A.id).update(
		aliased_to=None
	),
	RequestActions.TAGWORK_DEPRECATE: lambda A, B: TagWork.objects.filter(
		id=A.id
	).update(deprecated=True),
	RequestActions.TAGWORK_UNDEPRECATE: lambda A, B: TagWork.objects.filter(
		id=A.id
	).update(deprecated=False),
	RequestActions.TAGWORK_PARENT: lambda A, B: TagWorkParenthood.objects.create(
		tag=A, parent=B
	),
	RequestActions.TAGWORK_UNPARENT: lambda A, B: TagWorkParenthood.objects.get(
		tag=A, parent=B
	).delete(),
	# RequestActions.WORKSOURCE_ATTACHTAG: lambda A, B: (
	# 	A.media.tags.add(B) if A.media else ...
	# ),
	# RequestActions.MEDIAWORK_ATTACHTAG: lambda A, B: A.tags.add(B),
}

request_router = Router()


@request_router.post('new', auth=django_auth, response=int)
@transaction.atomic
def make_bulk(request: HttpRequest, s: str):
	lines = [line for line in s.splitlines() if line.strip()]
	bulk = BulkRequest.objects.create(user=request.user)
	if not lines:
		raise Exception
	reqs = []
	for _, line in enumerate(lines):
		c = line.split()
		cmd, A_validator, Bs_validator = COMMANDS[c[0]]
		A = A_validator(c[1])
		assert (not c[2:] and not Bs_validator) or (c[2:] and Bs_validator)
		for arg, v in zip(c[2:], Bs_validator):
			reqs.append(UserRequest(bulk=bulk, command=cmd, A=A, B=v(arg)))
	UserRequest.objects.bulk_create(reqs)
	Subscription.objects.create(entity=bulk, subscriber=request.user)
	return bulk.id


@request_router.post('confirm', auth=django_auth)
@user_is_editor
@track_revision
def confirm(request: HttpRequest, request_id: int, status: Status):
	bulk = get_object_or_404(BulkRequest, id=request_id, status=Status.PENDING)
	match status:
		case Status.APPROVED:
			add_revision_message(f'Via request {bulk.id} from {bulk.user.username}')
			for r in bulk.requests.all():
				ACTIONS[r.command](r.A, r.B)
		case Status.UNAPPROVED:
			pass
		case Status.PENDING:
			pass
	bulk.status = status
	bulk.processed_by = request.user
	bulk.save()


class RequestSchema(ModelSchema):
	A: tuple[str, Union[*ENTITY_SCHEMAS]]
	B: tuple[str, Union[*ENTITY_SCHEMAS]]

	class Meta:
		model = UserRequest
		fields = ['command']

	@field_validator('A', mode='before', check_fields=False)
	@classmethod
	def A_validator(cls, value) -> str:
		return ContentType.objects.get_for_model(value).model, value

	@field_validator('B', mode='before', check_fields=False)
	@classmethod
	def B_validator(cls, value) -> str:
		return ContentType.objects.get_for_model(value).model, value


class BulkRequestSchema(Schema):
	requests: list[RequestSchema]
	user: ProfileSchema
	processed_by: ProfileSchema | None
	status: Status


@request_router.get('request', response=BulkRequestSchema)
def user_request(request: HttpRequest, request_id: int):
	bulk = get_object_or_404(BulkRequest, id=request_id)
	return bulk
