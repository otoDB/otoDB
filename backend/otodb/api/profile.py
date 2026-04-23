from typing import List, Literal

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django_comments_xtd.models import XtdComment
from ninja import Field, FilterSchema, ModelSchema, Query, Router
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth
from pydantic import field_validator

from otodb.account.models import Account
from otodb.models import (
	Notification,
	Post,
	ProfileConnection,
	Revision,
	UserPreference,
	WorkSource,
)
from otodb.models.enums import (
	NotificationReason,
	Platform,
	Preferences,
	ProfileConnectionTypes,
	Status,
	WorkOrigin,
	WorkStatus,
)

from .comment import ModelsWithComments
from .common import (
	AuthedHttpRequest,
	ConnectionSchema,
	ListSchema,
	ProfileSchema,
	UserPreferenceSchema,
	WorkSourceSchema,
	make_alt_value_parser,
	profile_connection_parsers,
)

profile_router = Router()


@profile_router.get('profile', response=ProfileSchema)
def profile(request: AuthedHttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user


class ProfileIndexSchema(ModelSchema):
	id: int
	level: Account.Levels
	works_count: int
	revisions_count: int
	posts_count: int
	comments_count: int

	class Meta:
		model = Account
		fields = ['username', 'date_created']


class ProfileSearchFilterSchema(FilterSchema):
	username: str | None = Field(None, json_schema_extra={'q': 'username__icontains'})
	level: Account.Levels | None = None


@profile_router.get('search', response=List[ProfileIndexSchema])
@paginate
def search(
	request: AuthedHttpRequest,
	filters: ProfileSearchFilterSchema = Query(...),
	order: Literal[
		'username',
		'-username',
		'date_created',
		'-date_created',
		'level',
		'-level',
		'works_count',
		'-works_count',
		'revisions_count',
		'-revisions_count',
		'posts_count',
		'-posts_count',
		'comments_count',
		'-comments_count',
	] = '-date_created',
):
	post_ct = ContentType.objects.get_for_model(Post)

	works_count = (
		WorkSource.objects.filter(added_by=OuterRef('pk'))
		.values('added_by')
		.annotate(c=Count('media', distinct=True))
		.values('c')
	)
	revisions_count = (
		Revision.objects.filter(user=OuterRef('pk'))
		.values('user')
		.annotate(c=Count('id'))
		.values('c')
	)
	op_posts_count = (
		Post.objects.filter(added_by=OuterRef('pk'))
		.values('added_by')
		.annotate(c=Count('id'))
		.values('c')
	)
	post_comments_count = (
		XtdComment.objects.filter(
			user=OuterRef('pk'), content_type=post_ct, is_removed=False
		)
		.order_by()
		.values('user')
		.annotate(c=Count('id'))
		.values('c')
	)
	other_comments_count = (
		XtdComment.objects.filter(user=OuterRef('pk'), is_removed=False)
		.exclude(content_type=post_ct)
		.order_by()
		.values('user')
		.annotate(c=Count('id'))
		.values('c')
	)

	qs = (
		Account.objects.filter(is_active=True)
		.annotate(
			works_count=Coalesce(Subquery(works_count, output_field=IntegerField()), 0),
			revisions_count=Coalesce(
				Subquery(revisions_count, output_field=IntegerField()), 0
			),
			_op_posts=Coalesce(
				Subquery(op_posts_count, output_field=IntegerField()), 0
			),
			_post_comments=Coalesce(
				Subquery(post_comments_count, output_field=IntegerField()), 0
			),
			comments_count=Coalesce(
				Subquery(other_comments_count, output_field=IntegerField()), 0
			),
		)
		.annotate(posts_count=F('_op_posts') + F('_post_comments'))
	)
	qs = filters.filter(qs)
	return qs.order_by(order, 'id')


@profile_router.get('lists', response=List[ListSchema])
def lists(request: AuthedHttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user.pool_set


class UserConnectionSchema(ConnectionSchema):
	site: ProfileConnectionTypes


@profile_router.get('connection', response=List[UserConnectionSchema])
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
	platform: Platform | None = None
	origin: WorkOrigin | None = Field(None, json_schema_extra={'q': 'work_origin'})
	status: WorkStatus | None = Field(None, json_schema_extra={'q': 'work_status'})


@profile_router.get('submissions', response=List[SourceSubmissionSchema])
@paginate
def submissions(
	request: AuthedHttpRequest,
	username: str,
	filters: SubmissionsFilterSchema = Query(...),
	order: Literal['id', '-id', 'published_date', '-published_date'] | None = '-id',
	standing: Status = Status.APPROVED,
):
	match standing:
		case Status.PENDING:
			q = Q(is_pending=True) | Q(media__status=Status.PENDING)
		case Status.APPROVED:
			q = Q(media__status=Status.APPROVED, is_pending=False)
		case Status.UNAPPROVED:
			q = Q(media__isnull=True, is_pending=False) | Q(
				media__status=Status.UNAPPROVED
			)

	user = get_object_or_404(Account, username__iexact=username)
	submissions = user.worksource_set.filter(q).select_related('media')
	filters.filter(submissions)
	return submissions.order_by(order)


@profile_router.post('prefs', auth=django_auth)
def set_prefs(request: AuthedHttpRequest, payload: UserPreferenceSchema):
	UserPreference.objects.bulk_create(
		[
			UserPreference(
				user=request.user,
				setting=getattr(Preferences, attr),
				value=value,
			)
			for attr, value in payload.dict().items()
			if value is not None
		],
		unique_fields=['user', 'setting'],
		update_conflicts=True,
		update_fields=['value'],
	)


class NotificationSchema(ModelSchema):
	id: int
	comment: tuple[ModelsWithComments, int | str] | None
	post: int | None = Field(None, alias='post_id')
	reason: NotificationReason

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
		raise HttpError(400, 'Bad Request')


@profile_router.delete('notification', auth=django_auth)
def del_notif(request: AuthedHttpRequest, notif_id: int):
	if request.user.notifs.filter(id=notif_id).delete()[0] > 0:
		return 200
	else:
		raise HttpError(400, 'Bad Request')
