import re
import xml.etree.ElementTree as etree
from urllib.parse import quote

import nh3
from markdown import Extension
from markdown import markdown as _md
from markdown.inlinepatterns import InlineProcessor
from markdown.util import AtomicString
from markdownfield.models import EXTENSION_CONFIGS, EXTENSIONS
from markdownfield.validators import VALIDATOR_CLASSY


# fmt: off
_ENTITIES = [
	# name,   short_prefix, long_label,  url_path
	( 'work', 'w',          'work',      'work'     ),
	( 'list', 'l',          'list',      'list'     ),
	( 'rev',  'r',          'revision',  'revision' ),
]
# fmt: on

_ALLOWED_TAGS = (
	set(VALIDATOR_CLASSY.allowed_tags)
	| {
		'table',
		'thead',
		'tbody',
		'tr',
		'th',
		'td',
	}
) - {'img'}
_ALLOWED_ATTRIBUTES = {
	k: set(v) for k, v in VALIDATOR_CLASSY.allowed_attrs.items() if k != 'img'
} | {
	'td': {'align'},
	'th': {'align'},
}

_TRAILING_URL_PUNCTUATION = ';,.!?)]<>'

_MENTION_QUOTED_PATTERN = r'(?<![\w/])@"([^"\n]+)"'
_MENTION_SIMPLE_PATTERN = r'(?<![\w/.])@(\w+)(?!\w)'
_MENTION_QUOTED_RE = re.compile(_MENTION_QUOTED_PATTERN)
_MENTION_SIMPLE_RE = re.compile(_MENTION_SIMPLE_PATTERN)

_TAG_REF_PATTERN = r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
_BARE_URL_PATTERN = r'(https?://[^\s<>\[\]"\']+)'
_SHORT_REF_PATTERN_TEMPLATE = r'(?<![/\w]){prefix}(\d+)(?!\w)'
_LONG_REF_PATTERN_TEMPLATE = r'(?i)(?<!\w){label}\s+#(\d+)(?!\w)'


def render_markdown(text: str) -> str:
	"""Render markdown to sanitized HTML."""
	dirty = _md(text=text, extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS)
	return nh3.clean(dirty, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRIBUTES)


def parse_mentions(text: str) -> list[str]:
	"""Extract unique @mentions from markdown source text."""
	names: set[str] = set()
	for match in _MENTION_QUOTED_RE.finditer(text):
		username = match.group(1).strip()
		if username:
			names.add(username)

	without_quoted = _MENTION_QUOTED_RE.sub(' ', text)
	for match in _MENTION_SIMPLE_RE.finditer(without_quoted):
		names.add(match.group(1))

	return sorted(names)


def _quote_path(value: str) -> str:
	return quote(value, safe='')


class _RefProcessor(InlineProcessor):
	"""Base class for reference processors that generate <a> links."""

	def _make_link(self, href: str, text: str):
		el = etree.Element('a')
		el.set('href', href)
		# AtomicString prevents Python-Markdown from re-processing the text.
		el.text = AtomicString(text)
		return el


class _BareUrl(_RefProcessor):
	"""Bare URL auto-linker. Strips trailing punctuation."""

	def handleMatch(self, m, data):
		url = m.group(1)
		end = m.end(0)
		while url and url[-1] in _TRAILING_URL_PUNCTUATION:
			url = url[:-1]
			end -= 1
		el = self._make_link(url, url)
		return el, m.start(0), end


class _NumericRefShort(_RefProcessor):
	"""Short numeric reference like w123, l42, etc."""

	def __init__(self, pattern, md, prefix, url_path):
		super().__init__(pattern, md)
		self.prefix = prefix
		self.url_path = url_path

	def handleMatch(self, m, data):
		num = m.group(1)
		el = self._make_link(f'/{self.url_path}/{num}', f'{self.prefix}{num}')
		return el, m.start(0), m.end(0)


class _NumericRefLong(_RefProcessor):
	"""Long numeric reference like work #123, list #42, etc."""

	def __init__(self, pattern, md, label, url_path):
		super().__init__(pattern, md)
		self.label = label
		self.url_path = url_path

	def handleMatch(self, m, data):
		num = m.group(1)
		el = self._make_link(f'/{self.url_path}/{num}', f'{self.label} #{num}')
		return el, m.start(0), m.end(0)


class _TagRef(_RefProcessor):
	"""Tag wiki link: [[slug]] or [[slug|Display Text]]."""

	def handleMatch(self, m, data):
		slug = m.group(1).strip()
		display = m.group(2).strip() if m.group(2) else slug
		el = self._make_link(f'/tag/{_quote_path(slug)}', display)
		return el, m.start(0), m.end(0)


class _UserRefQuoted(_RefProcessor):
	"""Quoted user mention: @"username with spaces"."""

	def handleMatch(self, m, data):
		username = m.group(1)
		el = self._make_link(f'/profile/{_quote_path(username)}', f'@{username}')
		return el, m.start(0), m.end(0)


class _UserRefSimple(_RefProcessor):
	"""Simple user mention: @username."""

	def handleMatch(self, m, data):
		username = m.group(1)
		el = self._make_link(f'/profile/{_quote_path(username)}', f'@{username}')
		return el, m.start(0), m.end(0)


class OtoDBReferencesExtension(Extension):
	def extendMarkdown(self, md):
		priority = 175.0

		for name, short_prefix, long_label, url_path in _ENTITIES:
			md.inlinePatterns.register(
				_NumericRefShort(
					_SHORT_REF_PATTERN_TEMPLATE.format(prefix=re.escape(short_prefix)),
					md,
					prefix=short_prefix,
					url_path=url_path,
				),
				f'{name}_ref_short',
				priority,
			)
			priority -= 0.01

			md.inlinePatterns.register(
				_NumericRefLong(
					_LONG_REF_PATTERN_TEMPLATE.format(label=re.escape(long_label)),
					md,
					label=long_label,
					url_path=url_path,
				),
				f'{name}_ref_long',
				priority,
			)
			priority -= 0.01

		md.inlinePatterns.register(
			_TagRef(_TAG_REF_PATTERN, md),
			'tag_ref',
			priority,
		)
		priority -= 0.01

		md.inlinePatterns.register(
			_UserRefQuoted(_MENTION_QUOTED_PATTERN, md),
			'user_ref_quoted',
			priority,
		)
		priority -= 0.01

		md.inlinePatterns.register(
			_UserRefSimple(_MENTION_SIMPLE_PATTERN, md),
			'user_ref',
			priority,
		)
		priority -= 0.01

		md.inlinePatterns.register(
			_BareUrl(_BARE_URL_PATTERN, md),
			'bare_url',
			115,
		)


def makeExtension(**kwargs):
	return OtoDBReferencesExtension(**kwargs)
