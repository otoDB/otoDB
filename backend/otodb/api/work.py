from typing import List

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count

from simple_history.utils import update_change_reason

from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import video_info
from otodb.models import MediaWork, WorkRelation, WorkSource, TagWorkVote
from otodb.models.enums import Platform

from .common import WorkSchema, WorkSourceSchema, Error, TagWorkSchema, user_is_trusted, user_is_moderator

work_router = Router()

class ExternalQuery(Schema):
    work_id: int
    tags: List[TagWorkSchema]

@work_router.get('query_external', response=ExternalQuery)
def query_external(request: HttpRequest, platform: str, id: str):
    work = get_object_or_404(WorkSource.active_objects, platform=Platform.from_str(platform), source_id=id)
    return { 'tags': work.media.tags, 'work_id': work.media.id }

@work_router.get('search', response=List[WorkSchema])
@paginate
def search(request: HttpRequest, query: str):
    return MediaWork.active_objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

@work_router.get('work', response=WorkSchema)
def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    return work

class TagWorkInstanceSchema(Schema):
    tag_slug: str
    n_votes: int
    score: float
    user_score: int | None

@work_router.get('tag_scores', response=List[TagWorkInstanceSchema])
@user_is_trusted
def get_tag_scores(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    user_votes = TagWorkVote.objects.filter(user=request.user, tag_instance__in=work.tagworkinstance_set.all())
    return [{
        'tag_slug': instance.work_tag.slug,
        'score': instance.avg_score,
        'n_votes': instance.n_votes,
        'user_score': user_votes.filter(tag_instance=instance).values_list('score', flat=True).first()
        } for instance in work.tagworkinstance_set.annotate(avg_score=Avg('tagworkvote__score', default=0), n_votes=Count('tagworkvote')).all()]

class TagWorkVoteSchema(Schema):
    tag_slug: str
    score: int

@work_router.put('tag_scores')
@user_is_trusted
def vote_tags(request: HttpRequest, work_id: int, payload: List[TagWorkVoteSchema]):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)

    for vote in payload:
        vote.score = max(-1, min(1, vote.score)) # zero trust

    work.tags.add(*[v.tag_slug for v in payload])

    for vote in payload:
        tag_instance = work.tagworkinstance_set.get(work_tag__slug=vote.tag_slug)
        if v := tag_instance.tagworkvote_set.filter(user=request.user).first():
            v.score = vote.score
            v.save()
        else:
            TagWorkVote.objects.create(tag_instance=tag_instance, user=request.user, score=vote.score)

    return 200

@work_router.get('random', response=WorkSchema)
def random(request: HttpRequest):
    return MediaWork.active_objects.random()

class IDSchema(Schema):
    id: int

class SlimWorkSchema(ModelSchema):
    class Meta:
        model = MediaWork
        fields = ['id', 'title', 'thumbnail']

class WorkRelationSchema(ModelSchema):
    A: IDSchema
    B: IDSchema
    class Meta:
        model = WorkRelation
        fields = ['relation']

@work_router.get('relations', response=tuple[list[WorkRelationSchema], list[SlimWorkSchema]])
def relations(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    relations, works = WorkRelation.get_component_from_work(work)
    return 200, (relations, works)

@work_router.post('relation', auth=django_auth)
@user_is_trusted
def relation(request: HttpRequest, payload: WorkRelationSchema):
    A = MediaWork.active_objects.get(id=payload.A.id)
    B = MediaWork.active_objects.get(id=payload.B.id)
    try:
        rel = WorkRelation.objects.get(A, B)
        rel.A = A
        rel.B = B
        rel.relation = payload.relation
        rel.save()
    except WorkRelation.DoesNotExist:
        rel = WorkRelation.objects.create(A=A, B=B, relation=payload.relation)
    return

@work_router.delete('relation', auth=django_auth)
@user_is_trusted
def delete_relation(request: HttpRequest, A: int, B: int):
    A = MediaWork.active_objects.get(id=payload.A.id)
    B = MediaWork.active_objects.get(id=payload.B.id)
    rel = WorkRelation.objects.get(A, B)
    rel.delete()
    return



@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    return work.worksource_set

@work_router.post('refresh_source', auth=django_auth)
def refresh_source(request: HttpRequest, source_id: int):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    src.refresh()
    return

class WorkEditSchema(ModelSchema):
    class Meta:
        model = MediaWork
        fields = ['title', 'description', 'thumbnail', 'rating']

@work_router.post('merge', auth=django_auth)
@user_is_moderator
def merge_works(request:HttpRequest, from_work_id: int, to_work_id: int, payload: WorkEditSchema):
    MediaWork.merge(
        get_object_or_404(MediaWork.active_objects, id=to_work_id),
        get_object_or_404(MediaWork.active_objects, id=from_work_id),
        payload.title,
        payload.description,
        payload.thumbnail,
        payload.rating
    )
    return

@work_router.put('work', auth=django_auth)
@user_is_trusted
def update_work(request: HttpRequest, work_id: int, payload: WorkEditSchema, reason: str):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    for attr, value in payload.dict().items():
        setattr(work, attr, value)
    work.save()
    update_change_reason(work, reason)
    return

@work_router.post('source', auth=django_auth, response={200: int, 400: Error})
@user_is_trusted
def new_source_from_url(request: HttpRequest, url: str, is_reupload: bool):
    src = WorkSource.from_url(url, user=request.user, is_reupload=is_reupload)
    if src is not None:
        return src.id
    else:
        return 400, {'message': "Bad request, is the URL correct?"}

@work_router.post('assign_source', auth=django_auth, description='Pass in work_id=-1 if creating new work from source.', response=int)
@user_is_moderator
def assign_source_to_work(request: HttpRequest, source_id: int, work_id: int):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    assert(src.media is None and src.rejection_reason is None)

    info = video_info(src.url) # Hopefully still available!
    
    if work_id != -1:
        work = get_object_or_404(MediaWork.active_objects, id=work_id)
    else:
        work = MediaWork.objects.create(title=src.title, description=src.description, thumbnail=src.thumbnail)
    
    work.tags.add(*info.get('tags', []))

    src.media = work
    src.save()

    for pool in src.pool_set.all():
        pool.add_work(work.id)
        pool.pending_items.remove(src)

    return work.id

@work_router.post('reject_source', auth=django_auth)
@user_is_moderator
def reject_source(request: HttpRequest, source_id: int, reason: str):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    src.rejection_reason = request.user.username + ': ' + reason
    src.save()
    return

@work_router.get('unbound', auth=django_auth, response=List[WorkSourceSchema])
@user_is_moderator
def get_unbound_sources(request: HttpRequest, pending: bool):
    return WorkSource.objects.filter(media__isnull=True, rejection_reason__isnull=pending)
