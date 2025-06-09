import { m } from '$lib/paraglide/messages.js';

export const WorkTagCategory = [
	m.fresh_lower_rook_trip,
	m.next_bland_goldfish_heart,
	m.grand_nice_pony_belong,
	m.knotty_due_hamster_wave,
	m.empty_fresh_mare_jump,
	m.sad_next_jaguar_renew
];

export const SongTagCategory = [
	m.fresh_lower_rook_trip,
	m.cozy_awful_mule_enrich,
	m.crisp_red_canary_tickle,
	m.sad_next_jaguar_renew
];

export const Rating = [m.fresh_lower_rook_trip, m.sound_such_sloth_talk, m.mad_sound_walrus_tap];

export const Status = [m.such_actual_okapi_dare, m.spare_few_kudu_learn, m.stale_vexed_hare_pray];

export const WorkOrigin = [m.crisp_red_canary_tickle, m.lucky_still_vulture_work];

export const WorkStatus = [m.this_lime_porpoise_launch, m.dizzy_mellow_pug_spur];

export const Platform = ['Invalid', 'YouTube', 'Niconico', 'Bilibili', 'SoundCloud'];

export const WorkRelationTypes = [
	m.spry_muddy_sloth_radiate,
	m.inclusive_just_rabbit_succeed,
	m.full_gaudy_sloth_value,
	m.icy_raw_gazelle_heal
];

export const SongRelationTypes = [
	m.antsy_north_reindeer_radiate,
	m.bold_polite_myna_delight,
	m.light_caring_deer_coax,
	m.spry_muddy_sloth_radiate
];

export const UserLevel = {
	ANONYMOUS: 0,
	RESTRICTED: 10,
	MEMBER: 20,
	EDITOR: 40,
	ADMIN: 50,
	OWNER: 100,
	0: m.heroic_busy_shrimp_lend,
	10: m.fancy_formal_falcon_quell,
	20: m.drab_alive_midge_edit,
	40: m.tasty_spry_firefox_fall,
	50: m.silly_blue_felix_amuse,
	100: m.tangy_formal_lionfish_tap
};

export const Languages = {
	NOT_APPLICABLE: 0,
	en: 1,
	ja: 2,
	'zh-cn': 3,
	ko: 4,
	0: 'N/A',
	1: 'en',
	2: 'ja',
	3: 'zh-cn',
	4: 'ko'
};

export const LanguageNames = {
	en: 'English',
	ja: '日本語',
	'zh-cn': '简体中文',
	ko: '한국어',
	English: 'en',
	日本語: 'ja',
	简体中文: 'zh-cn',
	한국인: 'ko'
};

export const ProfileConnectionTypes = {
	WEBSITE: 0,
	NICONICO: 1,
	YOUTUBE: 2,
	BILIBILI: 3,
	TWITTER: 4,
	BLUESKY: 5,

	0: 'Website',
	1: 'Niconico',
	2: 'YouTube',
	3: 'Bilibili',
	4: 'Twitter',
	5: 'Bluesky'
};

export const ProfileConnectionLink = {
	0: (id: string) => id,
	1: (id: string) => `https://www.nicovideo.jp/user/${id}/`,
	2: (id: string) => `https://www.youtube.com/${id}`,
	3: (id: string) => `https://space.bilibili.com/${id}`,
	4: (id: string) => `https://twitter.com/${id}/`,
	5: (id: string) => `https://bsky.app/profile/${id}`
};

export const ProfileConnectionParsers = [
	(link: string) =>
		link.startsWith('http://') || link.startsWith('https://') ? link : undefined,
	(link: string) => link.match(/^https?:\/\/www\.nicovideo\.jp\/user\/(\d+)(?:\/)?$/)?.[1],
	(link: string) =>
		link.match(/^https?:\/\/www\.youtube\.com\/([^/?#]+(?:\/[^/?#]+)*)(?:\/)?$/)?.[1],
	(link: string) => link.match(/^https?:\/\/space\.bilibili\.com\/(\d+)(?:\/)?$/)?.[1],
	(link: string) =>
		link.match(/^https?:\/\/(?:twitter|x)\.com\/([A-Za-z0-9_]{1,15})(?:\/)?$/)?.[1],
	(link: string) => link.match(/^https?:\/\/bsky\.app\/profile\/(.+?)(?:\/*)$/)?.[1]
];

export const SongConnectionTypes = {
	VGMDB: 0,
	0: 'VGMdb',
	VOCADB: 1,
	1: 'VocaDB',
	DISCOGS: 2,
	2: 'Discogs',
	MUSICBRAINZ: 3,
	3: 'MusicBrainz',
	RATEYOURMUSIC: 4,
	4: 'Rate Your Music',
	DOJINMUSICINFO: 5,
	5: '同人音楽info',

	REMYWIKI: 20,
	20: 'RemyWiki',
	SILENTBLUE: 21,
	21: 'Silent Blue',
	ZENIUS: 22,
	22: 'Zenius -I- vanisher.com',

	NNDMEDLEYWIKI: 30,
	30: 'NND Medley Wiki'
};

export const SongConnectionLink = {
	0: (id: string) => `https://vgmdb.net/album/${id}`,
	1: (id: string) => `https://vocadb.net/S/${id}`,
	2: (id: string) => `https://www.discogs.com/master/${id}`,
	3: (id: string) => `https://musicbrainz.org/recording/${id}`,
	4: (id: string) => `https://rateyourmusic.com/song/${id}/`,
	5: (id: string) => `https://www.dojin-music.info/song/${id}`,
	20: (id: string) => `https://remywiki.com/${id}`,
	21: (id: string) => `https://silentblue.remywiki.com/${id}`,
	22: (id: string) => `https://zenius-i-vanisher.com/v5.2/songdb.php?songid=${id}`,
	30: (id: string) => `https://medley.bepis.io/wiki/${id}`
};

export const SongConnectionParsers = {
	0: (link: string) => link.match(/^https?:\/\/vgmdb\.net\/album\/(\d+)(?:\/*)?$/)?.[1],
	1: (link: string) => link.match(/^https?:\/\/vocadb\.net\/S\/(\d+)(?:\/*)?$/)?.[1],
	2: (link: string) => link.match(/^https?:\/\/www\.discogs\.com\/master\/(\d+)(?:\/*)?$/)?.[1],
	3: (link: string) =>
		link.match(/^https?:\/\/musicbrainz\.org\/recording\/([a-f0-9-]+)(?:\/*)?$/)?.[1],
	4: (link: string) => link.match(/^https?:\/\/rateyourmusic\.com\/song\/([^/]+)(?:\/+)?$/)?.[1],
	5: (link: string) => link.match(/^https?:\/\/www.dojin-music\.info\/song\/(\d+)(?:\/+)?$/)?.[1],
	20: (link: string) => link.match(/^https?:\/\/remywiki\.com\/(.+?)(?:\/*)?$/)?.[1],
	21: (link: string) => link.match(/^https?:\/\/silentblue\.remywiki\.com\/(.+?)(?:\/*)?$/)?.[1],
	22: (link: string) =>
		link.match(
			/^https?:\/\/zenius-i-vanisher\.com\/v5\.2\/songdb\.php\?songid=(\d+)(?:\/*)?$/
		)?.[1],
	30: (link: string) => link.match(/^https?:\/\/medley\.bepis\.io\/wiki\/(.+?)(?:\/*)?$/)?.[1]
};

export const TagWorkConnectionTypes = {
	WEBSITE: 0,
	0: 'Website',

	OTOMADWIKI: 1,
	1: 'otomad.wiki',
	OTOMADFANDOM: 2,
	2: '音MAD Wiki 2',

	NICOPEDIA: 20,
	20: 'Niconico Encyclopedia',
	PIXIV_DICT: 21,
	21: 'Pixiv Dictionary',
	WIKIPEDIAEN: 22,
	22: 'Wikipedia (en)',
	NAMUWIKI: 23,
	23: 'Namu Wiki',
	KNOWYOURMEME: 24,
	24: 'Know Your Meme'
};

export const TagWorkConnectionLink = {
	0: (id: string) => id,
	1: (id: string) => `https://otomad.wiki/${id}`,
	2: (id: string) => `https://otomad.fandom.com/ja/wiki/${id}`,
	20: (id: string) => `https://dic.nicovideo.jp/a/${id}`,
	21: (id: string) => `https://dic.pixiv.net/a/${id}/`,
	22: (id: string) => `https://en.wikipedia.org/wiki/${id}`,
	23: (id: string) => `https://namu.wiki/w/${id}`,
	24: (id: string) => `https://knowyourmeme.com/memes/subcultures/${id}`
};

export const TagWorkConnectionParsers = {
	0: (link: string) =>
		link.startsWith('http://') || link.startsWith('https://') ? link : undefined,
	1: (link: string) => link.match(/^https?:\/\/otomad\.wiki\/([^/?#]+)(?:\/)?$/)?.[1],
	2: (link: string) =>
		link.match(/^https?:\/\/otomad\.fandom\.com\/ja\/wiki\/([^/?#]+)(?:\/)?$/)?.[1],
	20: (link: string) => link.match(/^https?:\/\/dic\.nicovideo\.jp\/a\/([^/?#]+)(?:\/)?$/)?.[1],
	21: (link: string) => link.match(/^https?:\/\/dic\.pixiv\.net\/a\/([^/?#]+)(?:\/)?$/)?.[1],
	22: (link: string) =>
		link.match(/^https?:\/\/en\.wikipedia\.org\/wiki\/([^/?#]+)(?:\/)?$/)?.[1],
	23: (link: string) =>
		link.match(/^https?:\/\/(?:[a-z]{2,}\.)?namu\.wiki\/w\/([^/?#]+)(?:\/)?$/)?.[1],
	24: (link: string) =>
		link.match(/^https?:\/\/knowyourmeme\.com\/memes\/subcultures\/([^/?#]+)(?:\/)?$/)?.[1]
};

export const SourceConnectionTypes = {
	ANIKORE: 1,
	1: 'AniKore',
	BANGUMI: 2,
	2: 'Bangumi',
	ANIDB: 3,
	3: 'AniDB',
	MYANIMELIST: 4,
	4: 'MyAnimeList',
	ANILIST: 5,
	5: 'AniList',
	KITSU: 6,
	6: 'Kitsu',
	ANIMEPLANET: 7,
	7: 'Anime-Planet',

	IMDB: 20,
	20: 'IMDb',
	LETTERBOXD: 21,
	21: 'Letterboxd',

	VNDB: 40,
	40: 'vndb',
	EROGAMESCAPE: 41,
	41: 'ErogameScape'
};

export const SourceConnectionLink = {
	1: (id: string) => `https://www.anikore.jp/anime/${id}/`,
	2: (id: string) => `https://bangumi.tv/subject/${id}`,
	3: (id: string) => `https://anidb.net/anime/${id}`,
	4: (id: string) => `https://myanimelist.net/anime/${id}`,
	5: (id: string) => `https://anilist.co/anime/${id}`,
	6: (id: string) => `https://kitsu.io/anime/${id}`,
	7: (id: string) => `https://www.anime-planet.com/anime/${id}`,
	20: (id: string) => `https://www.imdb.com/title/${id}/`,
	21: (id: string) => `https://letterboxd.com/film/${id}/`,
	40: (id: string) => `https://vndb.org/${id}`,
	41: (id: string) =>
		`https://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/game.php?game=${id}`
};

export const SourceConnectionParsers = {
	1: (link: string) => link.match(/^https?:\/\/www\.anikore\.jp\/anime\/(\d+)(?:\/)?$/)?.[1],
	2: (link: string) => link.match(/^https?:\/\/bangumi\.tv\/subject\/(\d+)(?:\/)?$/)?.[1],
	3: (link: string) => link.match(/^https?:\/\/anidb\.net\/anime\/(\d+)(?:\/)?$/)?.[1],
	4: (link: string) => link.match(/^https?:\/\/myanimelist\.net\/anime\/(\d+)(?:\/)?$/)?.[1],
	5: (link: string) => link.match(/^https?:\/\/anilist\.co\/anime\/(\d+)(?:\/)?$/)?.[1],
	6: (link: string) => link.match(/^https?:\/\/kitsu\.io\/anime\/([^/?#]+)(?:\/)?$/)?.[1],
	7: (link: string) =>
		link.match(/^https?:\/\/www\.anime-planet\.com\/anime\/([^/?#]+)(?:\/)?$/)?.[1],
	20: (link: string) => link.match(/^https?:\/\/www\.imdb\.com\/title\/(\d+)(?:\/)?$/)?.[1],
	21: (link: string) => link.match(/^https?:\/\/letterboxd\.com\/film\/([^/?#]+)(?:\/)?$/)?.[1],
	40: (link: string) => link.match(/^https?:\/\/vndb\.org\/(v\d+)(?:\/)?$/)?.[1],
	41: (link: string) =>
		link.match(
			/^https?:\/\/erogamescape\.dyndns\.org\/~ap2\/ero\/toukei_kaiseki\/game\.php\?game=(\d+)$/
		)?.[1]
};
