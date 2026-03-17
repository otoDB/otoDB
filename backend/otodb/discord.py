import logging
from typing import Any, cast

import requests
from django.conf import settings
from django.tasks import task

logger = logging.getLogger(__name__)

WEBHOOK_URL: str | None = getattr(settings, 'OTODB_DISCORD_WEBHOOK_URL', None) or None
BASE_URL: str | None = (
	f'https://{settings.OTODB_FRONTEND_DOMAIN}'
	if getattr(settings, 'OTODB_FRONTEND_DOMAIN', None)
	else None
)
ENABLED = bool(WEBHOOK_URL and BASE_URL)

POST_EMOJI: dict[int, str] = {
	0: '📢',
	1: '💡',
	2: '🐛',
	3: '🌱',
}
POST_COLOR: dict[int, int] = {
	# Matches frontend tag colors
	0: 0xDC2626,  # red
	1: 0xE879F9,  # pink
	2: 0xFBBF24,  # orange
	3: 0x65A30D,  # green
}
DEFAULT_POST_COLOR = 0x0891B2
DEFAULT_COMMENT_COLOR = 0x9FA3A9
# Comments on posts (replies) will use Discord default color


def _send_webhook(embeds: list[dict[str, Any]]) -> None:
	payload = {
		'username': settings.OTODB_CONFIG_DICT['site_name'],
		'embeds': embeds,
	}
	try:
		resp = requests.post(cast(str, WEBHOOK_URL), json=payload, timeout=5)
		resp.raise_for_status()
	except Exception:
		logger.exception('Discord webhook failed')


def _entity_info(
	model_name: str, entity_pk: int, comment_pk: int | None = None
) -> tuple[str, str | None]:
	"""Return (display_label, url_or_None) for a commentable entity."""
	match model_name:
		case 'post':
			from otodb.models.posts import Post

			post_title: str | None = (
				Post.objects.filter(pk=entity_pk)
				.values_list('title', flat=True)
				.first()
			)
			label = post_title or f'post #{entity_pk}'
			url = f'{BASE_URL}/post/{entity_pk}'
			if comment_pk:
				url += f'#c{comment_pk}'
			return label, url
		case 'mediawork':
			from otodb.models.media import MediaWork

			title: str | None = (
				MediaWork.objects.filter(pk=entity_pk)
				.values_list('title', flat=True)
				.first()
			)
			label = f'{title} (work #{entity_pk})' if title else f'work #{entity_pk}'
			return label, f'{BASE_URL}/work/{entity_pk}'
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
			from otodb.account.models import Account

			username: str | None = (
				Account.objects.filter(pk=entity_pk)
				.values_list('username', flat=True)
				.first()
			)
			label = username or f'user #{entity_pk}'
			return label, f'{BASE_URL}/profile/{username}' if username else None
		case _:
			return f'{model_name} #{entity_pk}', None


@task
def discord_post(post_id: int, username: str) -> None:
	if not ENABLED:
		return

	from otodb.models.posts import Post, PostContent

	post = Post.objects.get(pk=post_id)
	content: PostContent = post.postcontent_set.earliest('pk')
	page: str = content.page
	description = (page[:2000] + '...') if len(page) > 2000 else page

	_send_webhook(
		[
			{
				'title': f'{POST_EMOJI.get(post.category, "")} {post.title}'.strip(),
				'description': description,
				'color': POST_COLOR.get(post.category, DEFAULT_POST_COLOR),
				'url': f'{BASE_URL}/post/{post.pk}',
				'timestamp': content.modified.isoformat(),
				'author': {
					'name': username,
					'url': f'{BASE_URL}/profile/{username}',
				},
			}
		]
	)


@task
def discord_comment(
	comment_id: int,
	model_name: str,
	entity_pk: int,
	username: str,
) -> None:
	if not ENABLED:
		return

	from django.contrib.contenttypes.models import ContentType
	from django_comments_xtd.models import XtdComment

	comment = XtdComment.objects.get(pk=comment_id)
	text: str = comment.comment
	description = (text[:2000] + '...') if len(text) > 2000 else text
	label, url = _entity_info(model_name, entity_pk, comment.pk)

	ct = ContentType.objects.get(model=model_name)
	comments = XtdComment.objects.filter(content_type=ct, object_pk=entity_pk)

	embed: dict[str, Any] = {
		'title': f'💬 {label}',
		'description': description,
		'timestamp': comment.submit_date.isoformat(),
		'author': {
			'name': username,
			'url': f'{BASE_URL}/profile/{username}',
		},
		'fields': [
			{
				'name': '↩️ Replies',
				'value': str(comments.count()),
				'inline': True,
			},
			{
				'name': '👥 Users',
				'value': str(comments.values('user').distinct().count()),
				'inline': True,
			},
		],
	}
	if url:
		embed['url'] = url
	if model_name != 'post':
		embed['color'] = DEFAULT_COMMENT_COLOR
	_send_webhook([embed])
