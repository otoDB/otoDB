from typing import List, Literal

from pydantic import field_validator

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from ninja import Router, FilterSchema, Query, Field, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.account.models import Account
from otodb.models import ProfileConnection, UserPreferences, Notification

from .common import (
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
def profile(request: HttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user


@profile_router.get('lists', response=List[ListSchema])
def lists(request: HttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user.pool_set


@profile_router.get('connection', response=List[ConnectionSchema])
def connection(request: HttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user.profileconnection_set


creator_tag_connection_parser = make_alt_value_parser(*profile_connection_parsers)


@profile_router.put('connection', auth=django_auth)
def edit_connections(request: HttpRequest, urls: str):
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
def work_in_lists(request: HttpRequest, work_id: int):
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
	request: HttpRequest,
	username: str,
	filters: SubmissionsFilterSchema = Query(...),
	order: Literal['id', '-id', 'published_date', '-published_date'] | None = '-id',
):
	user = get_object_or_404(Account, username__iexact=username)
	submissions = user.worksource_set.all().select_related('rejection', 'media')
	submissions = filters.filter(submissions)
	submissions = submissions.order_by(order)
	return submissions


@profile_router.post('prefs', auth=django_auth)
def set_prefs(request: HttpRequest, payload: UserPreferencesSchema):
	prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
	for attr, value in payload.dict().items():
		if value is not None:
			setattr(prefs, attr, value)
	prefs.save()


class NotificationSchema(ModelSchema):
	class Meta:
		model = Notification
		fields = ['message', 'dismissed']


@profile_router.get(
	'notifications', auth=django_auth, response=list[NotificationSchema]
)
def notifications(request: HttpRequest):
	return request.user.notifs
