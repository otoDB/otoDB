import re

from yt_dlp.extractor.twitter import TwitterIE
from yt_dlp.utils import traverse_obj

_MEDIA_TCO_RE = re.compile(r'\s*https?://t\.co/[0-9a-zA-Z]{10}$')


# 1: Surface note_tweet (full text + entity_set) for long tweets
_orig_graphql_to_legacy = TwitterIE._graphql_to_legacy


def _graphql_to_legacy(self, data, twid):
	status = _orig_graphql_to_legacy(self, data, twid)
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


# 2: Stash the raw status so _real_extract can rebuild description from it
_orig_extract_status = TwitterIE._extract_status


def _extract_status(self, twid):
	status = _orig_extract_status(self, twid)
	self._otodb_status = status if isinstance(status, dict) else None
	return status


# 3: Rebuild description with newlines preserved, links expanded, media t.co stripped
_orig_real_extract = TwitterIE._real_extract


def _real_extract(self, url):
	def _clean_tweet_text(text, entities):
		text = text or ''
		# Expand t.co shortlinks using data already in the GraphQL response
		for url in traverse_obj(entities, ('urls', ..., {dict})):
			short, expanded = url.get('url'), url.get('expanded_url')
			if short and expanded:
				text = text.replace(short, expanded)
		# Drop trailing media t.co (the only t.co left after expansion)
		return _MEDIA_TCO_RE.sub('', text)

	self._otodb_status = None
	info = _orig_real_extract(self, url)
	status = getattr(self, '_otodb_status', None)
	if isinstance(info, dict) and 'description' in info and status:
		note = status.get('note_tweet')
		if note:
			text, entities = note.get('text'), note.get('entity_set')
		else:
			text = status.get('full_text') or status.get('text')
			entities = status.get('entities')
		info['description'] = _clean_tweet_text(text, entities)
	return info


TwitterIE._graphql_to_legacy = _graphql_to_legacy
TwitterIE._extract_status = _extract_status
TwitterIE._real_extract = _real_extract
