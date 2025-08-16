from typing import List, Annotated

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, Value, Case, When, IntegerField

from simple_history.utils import update_change_reason

from pydantic import AfterValidator
from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth
from ninja.pagination import paginate

from otodb.common import video_info, NFKC
from otodb.models import MediaWork, WorkRelation, WorkSource, TagWorkVote, TagWorkInstance, WorkSourceRejection, TagWork
from otodb.models.enums import Platform, WorkOrigin, Rating, WorkTagCategory
from otodb.account.models import Account

from .common import WorkSchema, ThinWorkSchema, WorkSourceSchema, Error, TagWorkSchema, user_is_trusted, user_is_editor, RelationSchema, post_relation

work_router = Router()

class ExternalQuery(Schema):
    work_id: int
    tags: List[TagWorkSchema]

@work_router.get('query_external', response=ExternalQuery)
def query_external(request: HttpRequest, url: str | None = None, platform: str | None = None, id: str | None = None):
    if url:
        work = get_object_or_404(WorkSource.active_objects, url=url)
    elif platform and id:
        work = get_object_or_404(WorkSource.active_objects, platform=Platform.from_str(platform), source_id=id)
    else:
        # TODO: raise a more specific error
        raise ValueError("Either 'url' or both 'platform' and 'id' parameters must be provided")

    return { 'tags': work.media.tags, 'work_id': work.media.id }

@work_router.get('search', response=List[ThinWorkSchema])
@paginate
def search(request: HttpRequest, query: str, tags: str | None = None):
    search_id = int(query) if query.isdigit() else -1
    q = Q(title__icontains=query) | Q(description__icontains=query)
    if tags:
        for tag in tags.split():
            q = q & Q(tags__slug=NFKC(tag))
    else:
        q = q | Q(worksource__source_id=query)
        if query.startswith("https"):
            q = q | Q(worksource__url=query)
        if search_id > 0:
            q = q | Q(id=search_id)

    return MediaWork.active_objects.filter(q).annotate(
        priority=Case(
            When(id=search_id, then=Value(0)),
            When(worksource__url=query, then=Value(1)),
            When(worksource__source_id=query, then=Value(2)),
            When(Q(title__icontains=query) | Q(description__icontains=query), then=Value(100)),
            default=Value(1000),
            output_field=IntegerField()
        )
    ).order_by('priority', '-id').distinct()

@work_router.get('tags_needed', response=List[ThinWorkSchema])
@paginate
def tags_needed(request: HttpRequest):
    return MediaWork.active_objects.annotate(ntags=Count('tags', filter=Q(tags__deprecated=False))).filter(ntags__lte=2)

@work_router.get('work', response={ 200: WorkSchema, 300: int })
def work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.objects, id=work_id)
    if work.moved_to:
        return 300, work.moved_to.id
    return work

@work_router.delete('work', auth=django_auth)
@user_is_editor
def delete_work(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    work.worksource_set.update(media=None)
    work.delete()

class TagWorkInstanceSchema(Schema):
    tag_slug: str
    n_votes: int
    score: float
    user_score: int | None
    sample: bool
    creator_roles: List[int]

@work_router.get('tag_scores', response=List[TagWorkInstanceSchema], auth=django_auth)
@user_is_trusted
def get_tag_scores(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    user_votes = TagWorkVote.objects.filter(user=request.user, tag_instance__in=work.tagworkinstance_set.all())
    return [{
        'tag_slug': instance.work_tag.slug,
        'score': instance.avg_score,
        'n_votes': instance.n_votes,
        'user_score': user_votes.filter(tag_instance=instance).values_list('score', flat=True).first(),
        'sample': instance.used_as_source,
        'creator_roles': instance.get_creator_roles(),
        } for instance in work.tagworkinstance_set.annotate(avg_score=Avg('tagworkvote__score', default=0), n_votes=Count('tagworkvote')).all()]

class TagWorkVoteSchema(Schema):
    tag_slug: Annotated[str, AfterValidator(NFKC)]
    score: int

@work_router.put('tag_scores', auth=django_auth)
@user_is_trusted
def vote_tags(request: HttpRequest, work_id: int, payload: List[TagWorkVoteSchema]):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)

    for vote in payload:
        vote.score = max(-1, min(1, vote.score)) # zero trust

    tags = []
    for v in payload:
        try:
            tags.append(TagWork.objects.get(slug=v.tag_slug))
        except TagWork.DoesNotExist:
            tags.append(TagWork.objects.create(name=v.tag_slug))

    work.tags.add(*tags)

    for vote in payload:
        tag_instance = work.tagworkinstance_set.get(work_tag__slug=vote.tag_slug)
        if v := tag_instance.tagworkvote_set.filter(user=request.user).first():
            v.score = vote.score
            v.save()
        else:
            TagWorkVote.objects.create(tag_instance=tag_instance, user=request.user, score=vote.score)

    return 200


class CreatorRolesUpdateSchema(Schema):
	work_id: int
	tag_slug: str
	creator_roles: List[int]

@work_router.post('creator_roles', auth=django_auth)
@user_is_trusted
def update_creator_roles(request: HttpRequest, payload: CreatorRolesUpdateSchema):
	instance = get_object_or_404(TagWorkInstance, work_id=payload.work_id, work_tag__slug=payload.tag_slug)

	if instance.work_tag.category == WorkTagCategory.CREATOR:
		instance.set_creator_roles(payload.creator_roles)
		instance.save()

	return 200

@work_router.put('toggle_sample', auth=django_auth)
@user_is_trusted
def toggle_sample(request: HttpRequest, work_id: int, tag_slug: str):
    instance = get_object_or_404(TagWorkInstance, work_id=work_id, work_tag__slug=tag_slug)
    instance.used_as_source = not instance.used_as_source
    instance.save()

@work_router.put('remove_tag', auth=django_auth)
@user_is_trusted
def remove_tag(request: HttpRequest, work_id: int, tag_slug: str):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    tag = get_object_or_404(TagWork, slug=tag_slug)
    work.tags.remove(tag)
    if tag.can_be_deleted:
        tag.delete()

@work_router.get('random', response=list[ThinWorkSchema])
def random(request: HttpRequest, n: int = 1):
    return MediaWork.active_objects.filter(rating=Rating.GENERAL).order_by("?")[:min(n,20)]

@work_router.get('recent', response=list[ThinWorkSchema])
def recent(request: HttpRequest, n: int = 1):
    return MediaWork.active_objects.order_by('-id')[:min(n, 20)]

class SlimWorkSchema(ModelSchema):
    id: int
    class Meta:
        model = MediaWork
        fields = ['title', 'thumbnail']

@work_router.get('relations', response=tuple[list[RelationSchema], list[SlimWorkSchema]])
def relations(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    relations = WorkRelation.get_component(work.id)
    return 200, (relations, {w.id: w for r in relations for w in (r.A, r.B)}.values())

@work_router.post('relation', auth=django_auth)
@user_is_trusted
def relation(request: HttpRequest, payload: RelationSchema):
    post_relation(MediaWork, payload)
    return

@work_router.delete('relation', auth=django_auth)
@user_is_trusted
def delete_relation(request: HttpRequest, A: int, B: int):
    a = MediaWork.active_objects.get(id=A)
    b = MediaWork.active_objects.get(id=B)
    rel = WorkRelation.objects.get(a, b)
    rel.delete()
    return

@work_router.get('sources', response=List[WorkSourceSchema])
def sources(request: HttpRequest, work_id: int):
    work = get_object_or_404(MediaWork.active_objects, id=work_id)
    return work.worksource_set

@work_router.post('unbind_source', auth=django_auth)
@user_is_editor
def unbind_sources(request: HttpRequest, source_id: int):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    if src.media.worksource_set.count() == 1:
        src.media.delete()
    src.media = None
    src.save()

@work_router.put('source_origin', auth=django_auth)
@user_is_editor
def source_origin(request: HttpRequest, source_id: int, status: int):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    src.work_origin = WorkOrigin(status).value
    src.save()

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
@user_is_editor
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

@work_router.post('source', auth=django_auth, response={200: int | None, 400: Error, 409: Error})
@user_is_trusted
def new_source_from_url(request: HttpRequest, url: str, is_reupload: bool, rating: int = 0, work_id: int | None = None, original_url: str | None = None):
    """Creates a new source and, for editors, performs auto-validation as well as Work creation
    
    The priority for redirections/merging is:.

    The usage scenarios are as follows:
    - For non-editors:
        - Adding a new source leaves it in the approval queue, without creating a Work;
        - If `work_id` is provided, or either of the original/reupload Source already has a Work, the new sources are added to them;
            - If two out of three elements have works, the third element is added based on priority: `work_id` > `url` > `original_url`;
        - Adding an existing source redirects to the corresponding work;
        - Adding multiple sources, each with a different work, redirects based on priority: `work_id` > `url` > `original_url`;
        - For existing sources/works, corrections (`rating`/`is_reupload`) are ignored; 
    - For editors:
        - Adding a new source creates a new Work;
        - For existing sources/works, corrections (`rating`/`is_reupload`) are applied;
        - If any or all of `work_id`/`url`/`original_url` have different Works, a merge is performed based on priority: `work_id` > `url` > `original_url.
    """

    is_editor = request.user.level >= Account.Levels.EDITOR

    # === Source retrieval, common to all flows ===

    src, info = WorkSource.from_url(url, user=request.user, is_reupload=is_reupload)

    original_src, original_info = WorkSource.from_url(original_url, user=request.user, is_reupload=False)\
        if original_url else (None, None)
    
    if src is None or original_url and original_src is None:
        return 400, {'message': "Bad request, is the URL correct?"}

    if getattr(src, 'rejection', None) or getattr(original_src, 'rejection', None):
        return 400, {'message': "Bad Request, This source has already been rejected"}
    
        
    # === Work check: no work, and not editor ===

    none_have_work = not work_id and not getattr(src, 'media', None) and not getattr(original_src, 'media', None)
    if none_have_work and not is_editor:
        return
    
    # === Work check: both have  Works ===

    all_have_work = getattr(src, 'media', None) and getattr(original_src, 'media', None)
    if all_have_work and (src.media.id == original_src.media.id or not is_editor):
        return src.media.id

    # === Work check: editor flow or existing work found in request/sources ===

    if work_id:
        work = get_object_or_404(MediaWork.active_objects, id=work_id)
    elif src.media:
        work = get_object_or_404(MediaWork.active_objects, id=src.media.id)
    elif original_src and original_src.media is not None:
        work = get_object_or_404(MediaWork.active_objects, id=original_src.media.id)
    else:
        work = MediaWork.objects.create(title=src.title, description=src.description, thumbnail=src.thumbnail, rating=rating)

    sync_work_source(work, src, info, is_editor)
    if (original_src):
        sync_work_source(work, original_src, original_info, is_editor)

    # update_fields is necessary here because previous merges will change
    # the "media" field in a way that's not tracked by the current
    # object.
    if (is_editor):
        if (work.rating != rating): 
            work.rating = rating
            work.save(update_fields=['rating'])
        if (src.work_origin != WorkOrigin(is_reupload)): 
            src.work_origin = WorkOrigin(is_reupload)
            src.save(update_fields=['work_origin'])
        if (original_src and original_src.work_origin != WorkOrigin.AUTHOR):
            original_src.work_origin = WorkOrigin.AUTHOR
            original_src.save(update_fields=['work_origin'])

    return work.id

def sync_work_source(work: MediaWork, src: WorkSource, info, can_merge):
    """Syncs source data to its work
    
    - Syncs tags and assigns the source to a work if orphan source;
    - Merges the work if `can_merge` is passed and the source has an existing, different work id.
    - Does nothing if the source is already assigned to the work;
    """

    if not src.media:
        work.tags.add(*info.get('tags', []))
        src.media = work
        src.save()
    elif can_merge and src.media.id != work.id:
        MediaWork.merge(
            from_work=src.media,
            to_work=work,
            title=work.title,
            description=work.description,
            thumbnail=work.thumbnail,
            rating=work.rating
        )


@work_router.post('assign_source', auth=django_auth, description='Omit work_id if creating new work from source.', response=int)
@user_is_editor
def assign_source_to_work(request: HttpRequest, source_id: int, work_id: int | None = None):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    assert(src.media is None and not getattr(src, 'rejection', None))

    info, _ = video_info(src.url) # Hopefully still available!

    if work_id is not None:
        work = get_object_or_404(MediaWork.active_objects, id=work_id)
    else:
        work = MediaWork.objects.create(title=src.title, description=src.description, thumbnail=src.thumbnail)

    # Add them first in case they don't exist
    work.tags.add(*info.get('tags', []))
    tags = TagWork.objects.filter(name__in=info.get('tags', []))
    work.tagworkinstance_set.filter(work_tag__in=tags).update(instance_imported_from_source=True)

    src.media = work
    src.save()

    for pool in src.pool_set.all():
        pool.add_work(work.id)
        pool.pending_items.remove(src)

    return work.id

@work_router.post('reject_source', auth=django_auth)
@user_is_editor
def reject_source(request: HttpRequest, source_id: int, reason: str):
    src = get_object_or_404(WorkSource.active_objects, id=source_id)
    src.rejection = WorkSourceRejection.objects.create(source=src, by=request.user, reason=reason)
    src.save()
    return

@work_router.get('unbound', auth=django_auth, response=List[WorkSourceSchema])
@user_is_editor
def get_unbound_sources(request: HttpRequest, pending: bool):
    return WorkSource.objects.filter(media__isnull=True, rejection__isnull=pending)
