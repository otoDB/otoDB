import type { FaviconKey } from '$lib/ConnectionFavicon.svelte';

const HOSTNAME_TO_FAVICON_KEY: Record<string, FaviconKey> = {
	'www.nicovideo.jp': 'Niconico',
	'dic.nicovideo.jp': 'Niconico Encyclopedia',
	'www.youtube.com': 'YouTube',
	'space.bilibili.com': 'Bilibili',
	'twitter.com': 'Twitter',
	'bsky.app': 'Bluesky',
	'soundcloud.com': 'Soundcloud',
	'www.anikore.jp': 'AniKore',
	'bangumi.tv': 'Bangumi',
	'anidb.net': 'AniDB',
	'myanimelist.net': 'MyAnimeList',
	'anilist.co': 'AniList',
	'kitsu.io': 'Kitsu',
	'www.anime-planet.com': 'Anime-Planet',
	'www.imdb.com': 'IMDb',
	'letterboxd.com': 'Letterboxd',
	'vndb.org': 'vndb',
	'erogamescape.dyndns.org': 'ErogameScape',
	'vgmdb.net': 'VGMdb',
	'vocadb.net': 'VocaDB',
	'www.discogs.com': 'Discogs',
	'musicbrainz.org': 'MusicBrainz',
	'rateyourmusic.com': 'Rate Your Music',
	'www.dojin-music.info': '同人音楽info',
	'touhoudb.com': 'TouhouDB',
	'remywiki.com': 'RemyWiki',
	'silentblue.remywiki.com': 'Silent Blue',
	'zenius-i-vanisher.com': 'Zenius -I- vanisher.com',
	'medley.bepis.io': 'NND Medley Wiki',
	'modarchive.org': 'The Mod Archive',
	'otomad.wiki': 'otomad.wiki',
	'otomad.fandom.com': '音MAD Wiki 2',
	'dic.pixiv.net': 'Pixiv Dictionary',
	'en.wikipedia.org': 'Wikipedia (en)',
	'namu.wiki': 'Namu Wiki',
	'knowyourmeme.com': 'Know Your Meme'
};

export function extractUrl(url: string): null | FaviconKey {
	let hostname: string;
	try {
		hostname = new URL(url).hostname;
	} catch {
		return null;
	}

	return HOSTNAME_TO_FAVICON_KEY[hostname] ?? null;
}
