import json
import logging
import re

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.extractor.niconico import NiconicoIE
from yt_dlp.extractor.twitter import TwitterIE
from yt_dlp.postprocessor.common import PostProcessingError
from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor
from yt_dlp.utils import (
	ExtractorError,
	determine_ext,
	float_or_none,
	int_or_none,
	mimetype2ext,
	parse_iso8601,
	traverse_obj,
)

logger = logging.getLogger(__name__)

_MEDIA_TCO_RE = re.compile(r'\s*https?://t\.co/[0-9a-zA-Z]{10}$')


class NiconicoIECustom(NiconicoIE):
	# Support nico.ms short URLs and /shorts/ URLs
	_VALID_URL = r'https?://(?:(?:embed|sp|www\.)?nicovideo\.jp/(?:watch|shorts)|nico\.ms)/(?P<id>(?:[a-z]{2})?\d+)'


class TwitterIECustom(TwitterIE):
	"""Twitter extractor that preserves long-tweet text and cleans descriptions.

	yt-dlp truncates long tweets to the legacy 280-char ``full_text`` and leaves
	every link as a raw ``t.co`` shortlink. This override surfaces the
	``note_tweet`` payload for long tweets and rebuilds ``description`` with
	newlines preserved, links expanded, and the trailing media ``t.co`` stripped.
	"""

	@staticmethod
	def _clean_tweet_text(text, entities):
		text = text or ''
		# Expand t.co shortlinks using data already in the GraphQL response
		for url in traverse_obj(entities, ('urls', ..., {dict})):
			short, expanded = url.get('url'), url.get('expanded_url')
			if short and expanded:
				text = text.replace(short, expanded)
		# Drop trailing media t.co (the only t.co left after expansion)
		return _MEDIA_TCO_RE.sub('', text)

	# Surface note_tweet (full text + entity_set) for long tweets
	def _graphql_to_legacy(self, data, twid):
		status = super()._graphql_to_legacy(data, twid)
		if isinstance(status, dict):
			result = traverse_obj(data, ('tweetResult', 'result', {dict})) or {}
			if result.get('__typename') == 'TweetWithVisibilityResults':
				result = traverse_obj(result, ('tweet', {dict})) or {}
			note = traverse_obj(
				result, ('note_tweet', 'note_tweet_results', 'result', {dict})
			)
			if note:
				status['note_tweet'] = note
		return status

	# Stash raw status so _real_extract can rebuild description from it.
	# Keyed by tweet id
	_statuses = {}

	def _extract_status(self, twid):
		status = super()._extract_status(twid)
		if isinstance(status, dict):
			self._statuses[twid] = status
		return status

	# Rebuild description with newlines preserved, links expanded, media t.co stripped
	def _real_extract(self, url):
		twid = self._match_id(url)
		try:
			info = super()._real_extract(url)
		finally:
			status = self._statuses.pop(twid, None)
		if isinstance(info, dict) and 'description' in info and status:
			note = status.get('note_tweet')
			if note:
				text, entities = note.get('text'), note.get('entity_set')
			else:
				text = status.get('full_text') or status.get('text')
				entities = status.get('entities')
			info['description'] = self._clean_tweet_text(text, entities)
		return info


def probe_media(ie, url: str) -> tuple[int | None, int | None, float | None]:
	"""
	Probe a remote media URL with ffprobe, returning (width, height, duration).
	"""
	try:
		pp = FFmpegPostProcessor(ie._downloader)
		metadata = pp.get_metadata_object(
			url, opts=['-v', 'error', '-rw_timeout', '15000000']
		)
	except (PostProcessingError, ValueError, OSError) as e:
		logger.warning(f'ffprobe failed for {url}: {e}')
		return None, None, None

	video = (
		traverse_obj(
			metadata,
			('streams', lambda _, s: s.get('codec_type') == 'video'),
			get_all=False,
		)
		or {}
	)
	duration = traverse_obj(
		metadata,
		('format', 'duration', {float_or_none}),
		('streams', ..., 'duration', {float_or_none}),
		get_all=False,
	)
	return int_or_none(video.get('width')), int_or_none(video.get('height')), duration


class MisskeyBaseIE(InfoExtractor):
	"""
	Shared extractor for Misskey instances.
	Subclasses set _VALID_URL with a `host` and an `id` group.
	"""

	_VALID_URL = False

	def _real_extract(self, url):
		host, note_id = self._match_valid_url(url).group('host', 'id')
		note = self._download_json(
			f'https://{host}/api/notes/show',
			note_id,
			data=json.dumps({'noteId': note_id}).encode(),
			headers={'Content-Type': 'application/json'},
		)

		user = note.get('user') or {}
		if user.get('host') is not None:
			raise ExtractorError('Remote notes are not supported', expected=True)

		file = next(
			(
				f
				for f in (note.get('files') or [])
				if (f.get('type') or '').startswith(('video/', 'audio/'))
			),
			None,
		)
		if file is None:
			raise ExtractorError('Note has no video or audio attachment', expected=True)

		mime = file.get('type') or ''
		is_audio = mime.startswith('audio/')
		width, height, duration = probe_media(self, file['url'])

		description = '\n\n'.join(
			part for part in (note.get('cw'), note.get('text')) if part
		)
		return {
			'id': note_id,
			'title': None,
			'description': description,
			'tags': note.get('tags') or [],
			'timestamp': parse_iso8601(note.get('createdAt')),
			'uploader_id': user['username'],
			'uploader': user.get('name'),
			'thumbnail': file.get('thumbnailUrl'),
			'duration': round(duration) if duration is not None else None,
			'webpage_url': f'https://{host}/notes/{note_id}',
			'formats': [
				{
					'url': file['url'],
					'format_id': file['id'],
					'ext': mimetype2ext(mime) or determine_ext(file['url']),
					'width': width,
					'height': height,
					'vcodec': 'none' if is_audio else None,
					'acodec': None,
					'filesize': int_or_none(file.get('size')),
				}
			],
		}


class OtomadSiteIE(MisskeyBaseIE):
	IE_NAME = 'otomad.site'
	_VALID_URL = r'https?://(?P<host>otomad\.site)/notes/(?P<id>\w+)'
