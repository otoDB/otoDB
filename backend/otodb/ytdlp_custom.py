import re

from yt_dlp.extractor.niconico import NiconicoIE
from yt_dlp.extractor.twitter import TwitterIE
from yt_dlp.utils import traverse_obj

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
