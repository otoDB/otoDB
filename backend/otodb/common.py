import requests
import json
import html
import re
import logging
from time import mktime
from datetime import datetime
import unicodedata
from http.cookiejar import MozillaCookieJar
from django.utils.text import slugify

from furl import furl
import nh3

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.bilibili import BiliBiliIE, BilibiliFavoritesListIE
from yt_dlp.extractor.niconico import NiconicoIE, NiconicoPlaylistIE
from yt_dlp.extractor.youtube import YoutubeIE, YoutubeTabIE
from yt_dlp.extractor.soundcloud import SoundcloudIE, SoundcloudPlaylistIE
from yt_dlp.extractor.twitter import TwitterIE
from yt_dlp.extractor.acfun import AcFunVideoIE

from django.conf import settings

from .models.enums import Platform, MimeType

logger = logging.getLogger(__name__)


def NFKC(s: str):
	return unicodedata.normalize('NFKC', s)


def clean_tag(s: str):
	return NFKC(s).strip()


def canonicalize_tag(s: str):
	return clean_tag(s).lower().replace(' ', '_')


def slugify_tag(s: str):
	return slugify(canonicalize_tag(s), allow_unicode=True)


class NiconicoIECustom(NiconicoIE):
	# Support nico.ms short URLs
	_VALID_URL = r'https?://(?:(?:embed|sp|www\.)?nicovideo\.jp/watch|nico\.ms)/(?P<id>(?:[a-z]{2})?\d+)'


ydl_playlist = YoutubeDL(
	{'http_headers': {'Accept-Language': 'ja'}, 'extract_flat': True}, auto_init=True
)
for e in (
	YoutubeTabIE,
	NiconicoPlaylistIE,
	BilibiliFavoritesListIE,
	SoundcloudPlaylistIE,
):
	ydl_playlist.add_info_extractor(e)

ydl, jar = None, None


def reset_cookies(cookie_file=settings.COOKIES_FILE):
	global ydl, jar

	jar = MozillaCookieJar(cookie_file) if cookie_file else MozillaCookieJar()
	if cookie_file:
		try:
			jar.load()
		except OSError:
			pass

	opts = {'http_headers': {'Accept-Language': 'ja'}, 'noplaylist': True}
	if cookie_file:
		opts['cookiefile'] = cookie_file
	ydl = YoutubeDL(opts, auto_init=False)

	for e in (
		YoutubeIE,
		NiconicoIECustom,
		BiliBiliIE,
		SoundcloudIE,
		TwitterIE,
		AcFunVideoIE,
	):
		ydl.add_info_extractor(e)


reset_cookies()

platform_extractors: list[tuple[Platform, type[InfoExtractor]]] = [
	(Platform.YOUTUBE, YoutubeIE),
	(Platform.NICONICO, NiconicoIECustom),
	(Platform.BILIBILI, BiliBiliIE),
	(Platform.SOUNDCLOUD, SoundcloudIE),
	(Platform.TWITTER, TwitterIE),
	(Platform.ACFUN, AcFunVideoIE),
]  # type: ignore
make_video_url = {
	Platform.YOUTUBE: lambda s, uid=None: f'https://youtube.com/watch?v={s}',
	Platform.NICONICO: lambda s, uid=None: f'https://nicovideo.jp/watch/{s}',
	Platform.BILIBILI: lambda s, uid=None: (
		f'https://www.bilibili.com/video/{s + "/" if "_p" not in s else s[: s.index("_p")] + "/" + "?p=" + s[s.index("_p") + 2 :]}'
	),
	# TODO
	# Platform.SOUNDCLOUD: lambda s, uid=None: s,
	Platform.TWITTER: lambda s, uid=None: (
		f'https://twitter.com/{uid}/status/{s}'
		if uid
		else f'https://twitter.com/i/status/{s}'
	),
	Platform.ACFUN: lambda s, uid=None: (
		f'https://www.acfun.cn/v/{s if s.startswith("ac") else "ac" + s}'
	),
}

niconico_meta_re = re.compile(
	r'<meta name=\"server-response\" content=\"([ -~]*?)\" \/>'
)
hashtag_re = re.compile(r'#(\w+)')


def get_niconico_geoblocked(sm):
	clean_url = make_video_url[Platform.NICONICO](sm)
	r = requests.get(
		clean_url,
		headers={'User-Agent': 'Twitterbot/1.0', 'Accept-Language': 'ja'},
		cookies=jar,
	)
	if r.ok:
		if match := niconico_meta_re.search(r.text):
			res = json.loads(html.unescape(match.group(1)))['data']['response']
			return res
	return None


def process_video_info(full_info, link=None):
	"""
	Process raw video info from yt-dlp or niconico API into standardized format.

	Args:
	    full_info: Raw info dict from extractor
	    link: Original URL (optional, used for niconico processing)

	Returns:
	    Processed info dict or None if processing fails
	"""
	keys = {
		'extractor': 'site',
		'title': 'title',
		'description': 'description',
		'tags': 'tags',
		'width': 'work_width',
		'height': 'work_height',
		'duration': 'work_duration',
		'webpage_url': 'url',
		'id': 'id',
		'thumbnail': 'thumb',
		'thumbnail_mime': 'thumb_mime',
		'timestamp': 'timestamp',
		'uploader_id': 'uploader_id',
		'channel_id': 'channel_id',
	}

	try:
		# Handle niconico special case
		if 'video' in full_info and 'tag' in full_info:
			# This is a niconico geoblocked response
			if not link:
				return None
			link = (
				make_video_url[Platform.NICONICO](link)
				if not link.startswith('http')
				else link
			)
			max_res = max(
				full_info['media']['domand']['videos'], key=lambda s: s['width']
			)
			info = {
				'extractor': 'niconico',
				'title': full_info['video']['title'],
				'description': full_info['video']['description'],
				'tags': [x['name'] for x in full_info['tag']['items']],
				'width': max_res['width'],
				'height': max_res['height'],
				'duration': full_info['video']['duration'],
				'webpage_url': link,
				'id': full_info['video']['id'],
				'thumbnail': full_info['video']['thumbnail'].get(
					'ogp', full_info['video']['thumbnail']['url']
				),
				'timestamp': int(
					mktime(
						datetime.fromisoformat(
							full_info['video']['registeredAt']
						).timetuple()
					)
				),
				'uploader_id': full_info['owner']['id'] if full_info['owner'] else 0,
			}
		else:
			# Standard yt-dlp response
			info = full_info.copy()

			if info.get('_type') == 'playlist':
				info = info['entries'][0]  # TODO need some work...
			resolutions = [
				(f['width'], f['height'])
				for f in info['formats']
				if 'width' in f
				and f['width'] is not None
				# Exclude super-resolution (AI upscaled) formats
				and not f.get('format_id', '').endswith('-sr')
			]
			if resolutions:
				info['width'], info['height'] = max(resolutions, key=lambda s: s[0])

		info['extractor'] = Platform.from_str(info['extractor'])
		if info['extractor'] in make_video_url:
			info['webpage_url'] = make_video_url[info['extractor']](
				info['display_id']
				if info['extractor'] in [Platform.TWITTER]
				else info['id'],
				uid=info.get('uploader_id')
				if info['extractor'] in [Platform.TWITTER]
				else None,
			)

		# Platform-specific processing
		match info['extractor']:
			case Platform.YOUTUBE:
				info['tags'].extend(hashtag_re.findall(info['description']))
			case Platform.BILIBILI:
				if 'p' not in furl(info['webpage_url']).args:
					info['id'] = _clean_bilibili_source_id(info['id'])
					title_chapter_mark = info['title'].find(' p01')
					if title_chapter_mark != -1:
						info['title'] = info['title'][:title_chapter_mark]
					info['webpage_url'] = make_video_url[info['extractor']](info['id'])
				if 'tags' in info:
					info['tags'] = [
						tag[3:-1]
						if tag.startswith('发现《') and tag.endswith('》')
						else tag
						for tag in info['tags']
					]
			case Platform.NICONICO:
				pass  # webpage_url already set
			case Platform.SOUNDCLOUD:
				# TODO
				info['tags'] = list(
					set(info['tags'] + [info['genre']] + info['genres'])
				)
			case Platform.TWITTER:
				info['id'] = info['display_id']
				info['title'] = None
			case Platform.ACFUN:
				info['id'] = 'ac' + info['id']
			case _:
				return None

		# Clean up ID
		for c in ['?', '/']:  # drop query strings and subdirectories
			i = info['id'].find(c)
			if i != -1:
				info['id'] = info['id'][:i]

		# Process tags
		if 'tags' in info:
			info['tags'] = [canonicalize_tag(tag) for tag in info['tags']]

		# Clean description
		info['description'] = nh3.clean(info['description'])

		# Get thumbnail mime type
		info['thumbnail_mime'] = fetch_thumbnail_mime_type(info['thumbnail'])

		return {keys[key]: info[key] for key in keys if key in info}
	except Exception as e:
		logger.error(f'Error processing video info: {e}')
		return None


def video_info(link, expected_unavailable=False):
	try:
		if NiconicoIECustom.suitable(link):
			full_info = get_niconico_geoblocked(NiconicoIECustom.get_temp_id(link))
			if full_info:
				info = process_video_info(full_info, link)
				return info, full_info
			else:
				return None, None
		else:
			if not YoutubeIE.suitable(link) and YoutubeTabIE.suitable(link):
				f = furl(link)
				f.remove(['list'])
				link = f.url
				assert YoutubeIE.suitable(link)

			full_info = ydl.extract_info(link, download=False)
			info = process_video_info(full_info)
			return info, full_info
	except DownloadError as e:
		if expected_unavailable:
			logger.info(
				f'yt-dlp (expected) DownloadError extracting video info from {link}: {e}'
			)
		else:
			logger.error(f'yt-dlp DownloadError extracting video info from {link}: {e}')
		return None, None
	except Exception as e:
		logger.error(f'Error extracting video info from {link}: {e}')
		return None, None


def playlist_info(link):
	keys = {
		'title': 'title',
		'description': 'description',
		'entries': 'entries',
	}
	info = ydl_playlist.extract_info(link, download=False)
	if info.get('_type') != 'playlist':
		return None

	match info['extractor_key']:
		# Note: a platform may have multiple sorts of playlists that call different extractors
		case 'YoutubeTab':
			pass
		case 'NiconicoPlaylist':
			pass
		case 'BilibiliFavoritesList':
			pass
		case 'SoundcloudPlaylist':
			pass
		case _:
			return None

	info['entries'] = [entry['url'] for entry in info['entries']]

	return {keys[key]: info[key] for key in keys if key in info}


def _clean_bilibili_source_id(source_id: str) -> str:
	chapter_mark = source_id.find('_')
	return source_id[:chapter_mark] if chapter_mark != -1 else source_id


def fetch_thumbnail_mime_type(thumbnail_url: str):
	"""
	Fetch the MIME type of a thumbnail from its URL.

	Args:
	    thumbnail_url: URL of the thumbnail

	Returns:
	    MimeType enum value or None if fetch fails
	"""
	try:
		response = requests.get(thumbnail_url, allow_redirects=True, timeout=5)
		content_type = response.headers.get('Content-Type')
		return MimeType.from_str(content_type)
	except Exception as e:
		logger.error(f'Error fetching thumbnail mime type: {e}')
		return None
