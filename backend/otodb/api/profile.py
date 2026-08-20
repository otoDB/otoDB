import datetime
from collections import Counter
from typing import List, Literal

from django.core.cache import cache
from django.db.models import Count, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404
from django_comments_xtd.models import XtdComment
from ninja import Field, FilterSchema, ModelSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import django_auth
from pydantic import field_validator

from otodb.account.models import Account
from otodb.models import (
	ModerationEvent,
	Notification,
	ProfileConnection,
	Revision,
	RevisionChangeEntity,
	ThreadPost,
	UserPreference,
	WorkSource,
)
from otodb.models.enums import (
	FlagStatus,
	ModerationEventType,
	NotificationReason,
	OtodbIntegerEnum,
	Platform,
	Preferences,
	ProfileConnectionTypes,
	Route,
	Status,
	WorkOrigin,
	WorkStatus,
)

from .comment import ModelsWithComments
from .common import (
	AuthedHttpRequest,
	ConnectionSchema,
	ListSchema,
	OtodbID,
	ProfileSchema,
	UserPreferenceSchema,
	WorkSourceSchema,
	make_alt_value_parser,
	profile_connection_parsers,
)

profile_router = Router()


# Used for filters on submission page
class SubmissionStanding(OtodbIntegerEnum):
	PENDING = 0, 'Pending'
	APPROVED = 1, 'Approved'
	DELISTED = 2, 'Delisted'
	UNBOUND = 3, 'Unbound'
	FLAGGED = 4, 'Flagged'
	APPEALED = 5, 'Appealed'


@profile_router.get('profile', response=ProfileSchema)
def profile(request: AuthedHttpRequest, username: str):
	user = get_object_or_404(Account, username__iexact=username)
	return user


# Length of the contribution heatmap window, today included.
ACTIVITY_WINDOW_DAYS = 365
# The heatmap is expensive to compute and barely changes, so it is cached for an
# hour. `/api/profile` is excluded from the anonymous response cache (see
# otodb.middleware), so caching has to happen at the data level; that also keeps
# it working for logged-in viewers.
ACTIVITY_CACHE_TIMEOUT = 60 * 60


class ActivityDaySchema(Schema):
	date: datetime.date
	count: int


class ProfileActivitySchema(Schema):
	start: datetime.date
	end: datetime.date
	total: int
	days: list[ActivityDaySchema]


def _count_per_day(
	qs, field: str, since: datetime.datetime, until: datetime.datetime
) -> dict[datetime.date, int]:
	"""Count the rows of `qs` falling in [since, until), bucketed by UTC day.

	TIME_ZONE is left at Django's default, so the bucket boundaries have to be
	pinned to UTC explicitly to match the window the endpoint reports.
	"""
	rows = (
		qs.filter(**{f'{field}__gte': since, f'{field}__lt': until})
		.order_by()
		.annotate(day=TruncDate(field, tzinfo=datetime.UTC))
		.values('day')
		.annotate(n=Count('id'))
	)
	return {row['day']: row['n'] for row in rows}


def _compute_activity(user: Account) -> dict:
	end = datetime.datetime.now(datetime.UTC).date()
	start = end - datetime.timedelta(days=ACTIVITY_WINDOW_DAYS - 1)
	since = datetime.datetime.combine(start, datetime.time.min, tzinfo=datetime.UTC)
	until = since + datetime.timedelta(days=ACTIVITY_WINDOW_DAYS)

	counts: Counter[datetime.date] = Counter()
	# WorkSource uploads are revision-tracked, so counting them separately would
	# double count them.
	sources = (
		(Revision.objects.filter(user=user), 'date'),
		(ThreadPost.objects.filter(user=user, is_removed=False), 'created_at'),
		(XtdComment.objects.filter(user=user, is_removed=False), 'submit_date'),
	)
	for qs, field in sources:
		counts.update(_count_per_day(qs, field, since, until))

	# Serialized as ISO strings so the payload survives any cache backend's
	# serializer; the response schema parses them back into dates.
	return {
		'start': start.isoformat(),
		'end': end.isoformat(),
		'total': sum(counts.values()),
		'days': [
			{'date': day.isoformat(), 'count': counts[day]} for day in sorted(counts)
		],
	}


@profile_router.get('activity', response=ProfileActivitySchema)
def activity(request: AuthedHttpRequest, username: str):
	"""Daily contribution counts (revisions, thread posts and comments) over the
	last year, for the profile heatmap. Days with no activity are omitted."""
	user = get_object_or_404(Account, username__iexact=username)
	return cache.get_or_set(
		f'profile_activity:{user.pk}',
		lambda: _compute_activity(user),
		ACTIVITY_CACHE_TIMEOUT,
	)


class ProfileIndexSchema(ModelSchema):
	id: OtodbID
	level: Account.Levels
	works_count: int
	revisions_count: int
	posts_count: int
	comments_count: int
	date_created: datetime.datetime

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
	# Every thread message (opening posts and replies alike) is a ThreadPost.
	threadposts_count = (
		ThreadPost.objects.filter(user=OuterRef('pk'), is_removed=False)
		.order_by()
		.values('user')
		.annotate(c=Count('id'))
		.values('c')
	)
	other_comments_count = (
		XtdComment.objects.filter(user=OuterRef('pk'), is_removed=False)
		.order_by()
		.values('user')
		.annotate(c=Count('id'))
		.values('c')
	)

	qs = Account.objects.all().annotate(
		works_count=Coalesce(Subquery(works_count, output_field=IntegerField()), 0),
		revisions_count=Coalesce(
			Subquery(revisions_count, output_field=IntegerField()), 0
		),
		posts_count=Coalesce(
			Subquery(threadposts_count, output_field=IntegerField()), 0
		),
		comments_count=Coalesce(
			Subquery(other_comments_count, output_field=IntegerField()), 0
		),
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
def work_in_lists(request: AuthedHttpRequest, work_id: OtodbID):
	return [
		(lst, lst.work_in_pool(work_id).exists()) for lst in request.user.pool_set.all()
	]


class SourceSubmissionSchema(WorkSourceSchema):
	media: OtodbID | None
	media_status: Status | None = None

	@field_validator('media', mode='before', check_fields=False)
	@classmethod
	def work_id(cls, value) -> int | None:
		return value.id if value is not None else None

	@staticmethod
	def resolve_media_status(obj):
		return obj.media.status if obj.media else None


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
	standing: SubmissionStanding = SubmissionStanding.APPROVED,
):
	flagged_ids = ModerationEvent.objects.filter(
		event_type=ModerationEventType.FLAG, status=FlagStatus.PENDING
	).values_list('work_id', flat=True)
	appealed_ids = ModerationEvent.objects.filter(
		event_type=ModerationEventType.APPEAL, status=FlagStatus.PENDING
	).values_list('work_id', flat=True)

	match standing:
		case SubmissionStanding.PENDING:
			# Submitted and awaiting moderation: a pending work, or a source
			# binding awaiting editor approval.
			q = Q(is_pending=True) | Q(media__status=Status.PENDING)
		case SubmissionStanding.UNBOUND:
			# Uploaded but never attached to a work.
			q = Q(media__isnull=True, is_pending=False)
		case SubmissionStanding.FLAGGED:
			q = Q(
				is_pending=False,
				media__status=Status.APPROVED,
				media_id__in=flagged_ids,
			)
		case SubmissionStanding.APPEALED:
			q = Q(
				is_pending=False,
				media__status=Status.DELISTED,
				media_id__in=appealed_ids,
			)
		case SubmissionStanding.APPROVED:
			q = Q(is_pending=False, media__status=Status.APPROVED) & ~Q(
				media_id__in=flagged_ids
			)
		case SubmissionStanding.DELISTED:
			q = Q(is_pending=False, media__status=Status.DELISTED) & ~Q(
				media_id__in=appealed_ids
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
	id: OtodbID
	comment: tuple[ModelsWithComments, str] | None
	# (thread_id, post num); links to /thread/{id}.{num}
	threadpost: tuple[OtodbID, int] | None = None
	reason: NotificationReason
	revision_user: str | None = Field(None, alias='revision.user.username')
	revision_route: Route | None = None

	class Meta:
		model = Notification
		fields = ['dismissed', 'revision', 'created_at']

	@field_validator('comment', mode='before', check_fields=False)
	@classmethod
	def validate_comment(cls, value) -> tuple[ModelsWithComments, str] | None:
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
				else str(value.object_pk),
			)

	@field_validator('threadpost', mode='before', check_fields=False)
	@classmethod
	def validate_threadpost(cls, value) -> tuple[int, int] | None:
		if value is None:
			return None
		return (value.thread_id, value.num)


@profile_router.get(
	'notifications', auth=django_auth, response=list[NotificationSchema]
)
@paginate
def notifications(request: AuthedHttpRequest, subscription: bool | None = None):
	qs = (
		request.user.notifs.select_related('threadpost')
		.annotate(
			revision_route=Subquery(
				RevisionChangeEntity.objects.filter(
					change__rev_id=OuterRef('revision_id')
				).values('route')[:1]
			)
		)
		.order_by('dismissed', '-id')
	)
	if subscription is True:
		qs = qs.filter(revision__isnull=False)
	elif subscription is False:
		qs = qs.filter(revision__isnull=True)
	return qs


@profile_router.put('notification', auth=django_auth)
def read_notif(request: AuthedHttpRequest, notif_id: OtodbID):
	if request.user.notifs.filter(id=notif_id).update(dismissed=True) > 0:
		return 200
	else:
		raise HttpError(400, 'Bad Request')


@profile_router.delete('notification', auth=django_auth)
def del_notif(request: AuthedHttpRequest, notif_id: OtodbID):
	if request.user.notifs.filter(id=notif_id).delete()[0] > 0:
		return 200
	else:
		raise HttpError(400, 'Bad Request')
