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
	m.next_bland_goldfish_heart,
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
	0: 'Not Applicable',
	1: 'en',
	2: 'ja',
	3: 'zh-cn',
	4: 'ko'
};

export const LanguageNames = {
	en: 'English',
	ja: '日本語',
	'zh-cn': '简体中文',
	ko: '한국인',
	English: 'en',
	日本語: 'ja',
	简体中文: 'zh-cn',
	한국인: 'ko'
};

export const ProfileConnectionTypes = {
	Niconico: 0,
	YouTube: 1,
	Bilibili: 2,
	X: 3,
	Bluesky: 4,

	0: 'Niconico',
	1: 'YouTube',
	2: 'Bilibili',
	3: 'X',
	4: 'Bluesky'
};

export const ProfileConnectionLink = {
	0: (id: string) => `https://www.nicovideo.jp/user/${id}/`,
	1: (id: string) => `https://www.youtube.com/${id}`,
	2: (id: string) => `https://space.bilibili.com/${id}`,
	3: (id: string) => `https://twitter.com/${id}/`,
	4: (id: string) => `https://bsky.app/profile/${id}`
};

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
	20: (id: string) => `https://remywiki.com/${id}`,
	21: (id: string) => `https://silentblue.remywiki.com/${id}`,
	22: (id: string) => `https://zenius-i-vanisher.com/v5.2/songdb.php?songid=${id}`,
	30: (id: string) => `https://medley.bepis.io/wiki/${id}`
};

export const TagWorkConnectionTypes = {
	OTOMADWIKI: 1,
	1: 'otomad.wiki',
	OTOMADFANDOM: 2,
	2: 'Otomad Wiki 2',

	NICOPEDIA: 20,
	20: 'Niconico Encyclopedia',
	PIXIV_DICT: 21,
	21: 'Pixiv Dictionary',
	WIKIPEDIA: 22,
	22: 'Wikipedia',
	NAMUWIKI: 23,
	23: 'Namu Wiki',
	KNOWYOURMEME: 24,
	24: 'Know Your Meme',

	ANIKORE: 40,
	40: 'AniKore',
	BANGUMI: 41,
	41: 'Bangumi',
	ANIDB: 42,
	42: 'AniDB',
	MYANIMELIST: 43,
	43: 'MyAnimeList',

	WEBSITE: 0,
	0: 'Website'
};

export const TagWorkConnectionLink = {
	0: (id: string) => `https://${id}`,
	1: (id: string) => `https://otomad.wiki/${id}`,
	2: (id: string) => `https://otomad.fandom.com/ja/wiki/${id}`,
	20: (id: string) => `https://dic.nicovideo.jp/a/${id}`,
	21: (id: string) => `https://dic.pixiv.net/a/${id}/`,
	22: (id: string) => `https://en.wikipedia.org/wiki/${id}`,
	23: (id: string) => `https://namu.wiki/w/${id}`,
	24: (id: string) => `https://knowyourmeme.com/memes/subcultures/${id}`,
	40: (id: string) => `https://www.anikore.jp/anime/${id}/`,
	41: (id: string) => `https://bangumi.tv/subject/${id}`,
	42: (id: string) => `https://anidb.net/anime/${id}`,
	43: (id: string) => `https://myanimelist.net/anime/${id}`
};
