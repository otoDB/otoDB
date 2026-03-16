import logging
from typing import Any, cast

import requests
from django.conf import settings
from django.db import transaction
from django.tasks import task
from django_comments_xtd.models import XtdComment

from otodb.account.models import Account
from otodb.models.posts import Post, PostContent

logger = logging.getLogger(__name__)

WEBHOOK_URL: str | None = getattr(settings, 'OTODB_DISCORD_WEBHOOK_URL', None) or None
BASE_URL: str | None = (
	f'https://{settings.OTODB_FRONTEND_DOMAIN}'
	if getattr(settings, 'OTODB_FRONTEND_DOMAIN', None)
	else None
)
ENABLED = bool(WEBHOOK_URL and BASE_URL)


@task
def send_webhook(embeds: list[dict[str, Any]]) -> None:
	payload = {
		'username': settings.OTODB_CONFIG_DICT['site_name'],
		'embeds': embeds,
	}
	try:
		resp = requests.post(cast(str, WEBHOOK_URL), json=payload, timeout=5)
		resp.raise_for_status()
	except Exception:
		logger.exception('Discord webhook failed')


def _author(user: Account) -> dict[str, str]:
	return {
		'name': user.username,
		'url': f'{BASE_URL}/profile/{user.username}',
	}


def _entity_info(
	model_name: str, entity_pk: int, comment_pk: int | None = None
) -> tuple[str, str | None]:
	"""Return (display_label, url_or_None) for a commentable entity."""
	match model_name:
		case 'post':
			url = f'{BASE_URL}/post/{entity_pk}'
			if comment_pk:
				url += f'#c{comment_pk}'
			return f'post #{entity_pk}', url
		case 'mediawork':
			return f'work #{entity_pk}', f'{BASE_URL}/work/{entity_pk}'
		case 'pool':
			return f'pool #{entity_pk}', f'{BASE_URL}/list/{entity_pk}'
		case 'tagwork':
			from otodb.models.tag import TagWork

			slug: str | None = (
				TagWork.objects.filter(pk=entity_pk)
				.values_list('slug', flat=True)
				.first()
			)
			label = slug or f'tag #{entity_pk}'
			return label, f'{BASE_URL}/tag/{slug}' if slug else None
		case 'account':
			username: str | None = (
				Account.objects.filter(pk=entity_pk)
				.values_list('username', flat=True)
				.first()
			)
			label = username or f'user #{entity_pk}'
			return label, f'{BASE_URL}/profile/{username}' if username else None
		case _:
			return f'{model_name} #{entity_pk}', None


def discord_post(post: Post, user: Account) -> None:
	if not ENABLED:
		return

	content: PostContent = post.postcontent_set.earliest('pk')
	page: str = content.page
	description = (page[:2000] + '...') if len(page) > 2000 else page

	embed: dict[str, Any] = {
		'title': post.title,
		'description': description,
		'url': f'{BASE_URL}/post/{post.pk}',
		'timestamp': content.modified.isoformat(),
		'author': _author(user),
	}
	transaction.on_commit(lambda: send_webhook.enqueue([embed]))


def discord_comment(
	comment: XtdComment, model_name: str, entity_pk: int, user: Account
) -> None:
	if not ENABLED:
		return

	text: str = comment.comment
	description = (text[:2000] + '...') if len(text) > 2000 else text
	label, url = _entity_info(model_name, entity_pk, comment.pk)

	from django.contrib.contenttypes.models import ContentType

	ct = ContentType.objects.get(model=model_name)
	comments = XtdComment.objects.filter(content_type=ct, object_pk=entity_pk)

	embed: dict[str, Any] = {
		'title': f'Comment on {label}',
		'description': description,
		'timestamp': comment.submit_date.isoformat(),
		'author': _author(user),
		'fields': [
			{'name': 'Replies', 'value': str(comments.count()), 'inline': True},
			{
				'name': 'Users',
				'value': str(comments.values('user').distinct().count()),
				'inline': True,
			},
		],
	}
	if url:
		embed['url'] = url
	transaction.on_commit(lambda: send_webhook.enqueue([embed]))
