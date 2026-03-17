from typing import List, Literal

from pydantic import field_validator

from django.db.models import Q
from django.shortcuts import get_object_or_404

from ninja import Router, FilterSchema, Query, Field, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate
from ninja.errors import HttpError

from otodb.account.models import Account
from otodb.models import ProfileConnection, UserPreferences, Notification
from otodb.models.enums import Status

from .comment import ModelsWithComments

from .common import (
	AuthedHttpRequest,
	ListSchema,
	ProfileSchema,
	WorkSourceSchema,
	ConnectionSchema,
	UserPreferencesSchema,
	profile_connection_parsers,
	make_alt_value_parser,
)

profile_router = Router()


@profile_router.get('profile', response=ProfileSchema)
def profile(request: AuthedHttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user


@profile_router.get('lists', response=List[ListSchema])
def lists(request: AuthedHttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user.pool_set


@profile_router.get('connection', response=List[ConnectionSchema])
def connection(request: AuthedHttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user.profileconnection_set


creator_tag_connection_parser = make_alt_value_parser(*profile_connection_parsers)


@profile_router.put('connection', auth=django_auth)
def edit_connections(request: AuthedHttpRequest, urls: str):
	user = request.user
	ProfileConnection.objects.filter(profile=user).delete()
	urls = [
		creator_tag_connection_parser(url) for url in urls.split('\n') if url.strip()
	]
	urls = [url for url in urls if url]
	connections = [
		ProfileConnection(profile=user, site=site, content_id=content_id)
		for site, content_id in urls
	]
	ProfileConnection.objects.bulk_create(connections)


@profile_router.get(
	'work_in_my_lists', response=List[tuple[ListSchema, bool]], auth=django_auth
)
def work_in_lists(request: AuthedHttpRequest, work_id: int):
	return [
		(lst, lst.work_in_pool(work_id).exists()) for lst in request.user.pool_set.all()
	]


class SourceSubmissionSchema(WorkSourceSchema):
	media: int | None

	@field_validator('media', mode='before', check_fields=False)
	@classmethod
	def work_id(cls, value) -> str:
		return value.id if value is not None else None


class SubmissionsFilterSchema(FilterSchema):
	platform: int | None = None
	origin: int | None = Field(None, json_schema_extra={'q': 'work_origin'})
	status: int | None = Field(None, json_schema_extra={'q': 'work_status'})


@profile_router.get('submissions', response=List[SourceSubmissionSchema])
@paginate
def submissions(
	request: AuthedHttpRequest,
	username: str,
	filters: SubmissionsFilterSchema = Query(...),
	order: Literal['id', '-id', 'published_date', '-published_date'] | None = '-id',
	standing: int = 1,
):
	match Status(standing):
		case Status.PENDING:
			q = Q(is_pending=True)
		case Status.APPROVED:
			q = Q(media__isnull=False, is_pending=False)
		case Status.UNAPPROVED:
			q = Q(media__isnull=True, is_pending=False)

	user = get_object_or_404(Account, username__iexact=username)
	submissions = user.worksource_set.filter(q).select_related('media')
	filters.filter(submissions)
	return submissions.order_by(order)


@profile_router.post('prefs', auth=django_auth)
def set_prefs(request: AuthedHttpRequest, payload: UserPreferencesSchema):
	prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
	for attr, value in payload.dict().items():
		if value is not None:
			setattr(prefs, attr, value)
	prefs.save()


class NotificationSchema(ModelSchema):
	id: int
	comment: tuple[ModelsWithComments, int | str] | None
	post: int | None = Field(None, alias='post_id')

	class Meta:
		model = Notification
		fields = ['dismissed', 'revision']

	@field_validator('comment', mode='before', check_fields=False)
	@classmethod
	def cmt(cls, value) -> tuple[ModelsWithComments, int | str] | None:
		from otodb.models.tag import OtodbTagModel

		if value is None:
			return None
		else:
			ct = value.content_type
			T = ct.model_class()
			return (
				ct.model,
				T.objects.get(id=value.object_pk).slug
				if issubclass(T, OtodbTagModel)
				else int(value.object_pk),
			)


@profile_router.get(
	'notifications', auth=django_auth, response=list[NotificationSchema]
)
@paginate
def notifications(request: AuthedHttpRequest):
	return request.user.notifs.order_by('dismissed')


@profile_router.put('notification', auth=django_auth)
def read_notif(request: AuthedHttpRequest, notif_id: int):
	if request.user.notifs.filter(id=notif_id).update(dismissed=True) > 0:
		return 200
	else:
		raise HttpError(403, 'Forbidden')


@profile_router.delete('notification', auth=django_auth)
def del_notif(request: AuthedHttpRequest, notif_id: int):
	if request.user.notifs.filter(id=notif_id).delete()[0] > 0:
		return 200
	else:
		raise HttpError(403, 'Forbidden')
