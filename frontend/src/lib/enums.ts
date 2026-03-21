import { m } from '$lib/paraglide/messages.js';

export const WorkTagCategory = [
	m.fresh_lower_rook_trip,
	m.next_bland_goldfish_heart,
	m.grand_nice_pony_belong,
	m.knotty_due_hamster_wave,
	m.empty_fresh_mare_jump,
	m.sad_next_jaguar_renew,
	m.wise_keen_beaver_pick
];

export const WorkTagCategoriesSettableAsSource = [2, 4, 6];
export const WorkTagPresentationOrder = [1, 4, 6, 3, 2, 0, 5];
export const WorkTagPresentationColours = [
	'rgb(159,163,169)',
	'rgb(8,145,178)',
	'rgb(232,121,249)',
	'rgb(101,163,13)',
	'rgb(220,38,38)',
	'rgb(251,191,36)',
	'rgb(112,26,117)'
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

export const MimeType = {
	1: 'image/jpeg',
	2: 'image/png',
	3: 'image/webp'
};

export const Platform = [
	'Invalid',
	'YouTube',
	'Niconico',
	'Bilibili',
	'SoundCloud',
	'Twitter',
	'AcFun'
];

export const WorkRelationTypes = [
	m.spry_muddy_sloth_radiate,
	m.inclusive_just_rabbit_succeed,
	m.full_gaudy_sloth_value,
	m.icy_raw_gazelle_heal
];

export const WorkRelationEditorPredicate = [
	m.curly_many_orangutan_grip,
	m.sound_funny_hound_embrace,
	m.shy_bland_bird_harbor,
	m.major_tense_fly_savor
];

export const WorkRelationDisplayForward = [
	m.free_mellow_tiger_cook,
	m.dizzy_true_florian_pop,
	m.safe_gray_cowfish_dart,
	m.icy_raw_gazelle_heal
];

export const WorkRelationDisplayBackward = [
	m.spry_muddy_sloth_radiate,
	m.simple_fair_mallard_roar,
	m.full_gaudy_sloth_value,
	m.lazy_awful_gopher_build
];

export const SongRelationTypes = [
	m.antsy_north_reindeer_radiate,
	m.bold_polite_myna_delight,
	m.light_caring_deer_coax,
	m.spry_muddy_sloth_radiate
];

export const SongRelationPredicate = [
	m.frail_nimble_tadpole_arrive,
	m.mellow_only_bulldog_arise,
	m.giant_petty_shad_exhale,
	m.curly_many_orangutan_grip
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
	SOUNDCLOUD: 6,

	0: 'Website',
	1: 'Niconico',
	2: 'YouTube',
	3: 'Bilibili',
	4: 'Twitter',
	5: 'Bluesky',
	6: 'Soundcloud'
};

export const ProfileConnectionLink = {
	0: (id: string) => id,
	1: (id: string) => `https://www.nicovideo.jp/user/${id}/`,
	2: (id: string) => `https://www.youtube.com/${id}`,
	3: (id: string) => `https://space.bilibili.com/${id}`,
	4: (id: string) => `https://twitter.com/${id}/`,
	5: (id: string) => `https://bsky.app/profile/${id}`,
	6: (id: string) => `https://soundcloud.com/${id}`
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
	DOJINMUSICINFO: 5,
	5: '同人音楽info',
	TOUHOUDB: 6,
	6: 'TouhouDB',

	REMYWIKI: 20,
	20: 'RemyWiki',
	SILENTBLUE: 21,
	21: 'Silent Blue',
	ZENIUS: 22,
	22: 'Zenius -I- vanisher.com',

	NNDMEDLEYWIKI: 30,
	30: 'NND Medley Wiki',

	MODARCHIVE: 40,
	40: 'The Mod Archive'
};

export const SongConnectionLink = {
	0: (id: string) => `https://vgmdb.net/album/${id}`,
	1: (id: string) => `https://vocadb.net/S/${id}`,
	2: (id: string) => `https://www.discogs.com/master/${id}`,
	3: (id: string) => `https://musicbrainz.org/recording/${id}`,
	4: (id: string) => `https://rateyourmusic.com/song/${id}/`,
	5: (id: string) => `https://www.dojin-music.info/song/${id}`,
	6: (id: string) => `https://touhoudb.com/S/${id}`,
	20: (id: string) => `https://remywiki.com/${id}`,
	21: (id: string) => `https://silentblue.remywiki.com/${id}`,
	22: (id: string) => `https://zenius-i-vanisher.com/v5.2/songdb.php?songid=${id}`,
	30: (id: string) => `https://medley.bepis.io/wiki/${id}`,
	40: (id: string) => `https://modarchive.org/index.php?request=view_by_moduleid&query=${id}`
};

export const TagWorkConnectionTypes = {
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
	20: (id: string) => `https://dic.nicovideo.jp/${id}`,
	21: (id: string) => `https://dic.pixiv.net/a/${id}/`,
	22: (id: string) => `https://en.wikipedia.org/wiki/${id}`,
	23: (id: string) => `https://namu.wiki/w/${id}`,
	24: (id: string) => `https://knowyourmeme.com/${id}`
};

export const MediaConnectionTypes = {
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
	41: 'ErogameScape',

	VGMDB: 50,
	50: 'VGMdb'
};

export const MediaConnectionLink = {
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
		`https://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/game.php?game=${id}`,
	50: (id: string) => `https://vgmdb.net/product/${id}`
};

export const Role = {
	AUDIO: 1,
	1: m.weary_yummy_lobster_kick,
	VISUALS: 2,
	2: m.great_flaky_spider_comfort,
	DIRECTOR: 4,
	4: m.brief_slow_robin_fond,
	MUSIC: 8,
	8: m.known_green_jackal_jolt,
	ARTWORK: 16,
	16: m.weird_quaint_jan_dazzle,
	THANKS: 32,
	32: m.heavy_blue_parrot_mend
};

export const Themes = ['default', 'aniki', 'otogroove', 'retro-voyage', 'sorimix', 'resample'].map(
	(t) => 'theme-' + t
);

export const ThemeNames = [
	m.grassy_noble_walrus_wish,
	m.next_ago_opossum_swim,
	() => 'otogroove',
	m.tiny_plane_ape_pull,
	m.mean_zesty_ray_savor,
	() => 'Re:Sample'
];

export const HistoryModelNames = {
	mediawork: m.grand_merry_fly_succeed,
	workrelation: m.grand_merry_fly_succeed,
	worksource: m.grand_merry_fly_succeed,
	mediasong: m.grand_nice_pony_belong,
	songrelation: m.grand_nice_pony_belong,
	mediasongconnection: m.grand_nice_pony_belong,
	tagwork: m.empty_legal_chicken_taste,
	wikipage: m.curly_zesty_pelican_aim,
	tagworkconnection: m.empty_legal_chicken_taste,
	tagworkmediaconnection: m.empty_legal_chicken_taste,
	tagworkcreatorconnection: m.empty_legal_chicken_taste,
	tagworklangpreference: m.empty_legal_chicken_taste,
	tagworkparenthood: m.empty_legal_chicken_taste,
	tagsong: m.dull_plain_angelfish_cuddle
};

export const MediaType = {
	ANIME: 1,
	SHOW: 2,
	FILM: 4,
	GAME: 8,
	1: m.sea_new_barbel_rest,
	2: m.every_vivid_dolphin_dash,
	4: m.drab_gaudy_fly_relish,
	8: m.maroon_close_gorilla_bake
};

export const RequestActions = {
	1: 'worktag:alias',
	2: 'worktag:unalias',
	3: 'worktag:deprecate',
	4: 'worktag:undeprecate',
	5: 'worktag:parent',
	6: 'worktag:unparent'
};

export const PostCategories = [
	m.livid_loose_eel_pop,
	m.crazy_loud_trout_peek,
	m.new_honest_tapir_endure,
	m.moving_trick_piranha_thrive,
	m.fresh_lower_rook_trip
];

export const Route = {
	UNKNOWN: 0,
	TAGWORK_ALIAS: 1,
	TAGWORK_UNALIAS: 2,
	TAGWORK_DELETE: 3,
	TAGWORK_UPDATE: 4,
	TAGWORK_SET_BASE: 5,
	TAGWORK_ADD_LANG_PREF: 6,
	TAGWORK_EDIT_WIKI: 7,
	TAGWORK_EDIT_CONNECTIONS: 8,
	SONGTAG_UPDATE: 20,
	SONGTAG_SET_TAGS: 21,
	SONGRELATION_CREATE: 30,
	SONGRELATION_DELETE: 31,
	MEDIAWORK_DELETE: 40,
	MEDIAWORK_SET_TAGS: 41,
	MEDIAWORK_REMOVE_TAG: 42,
	MEDIAWORK_UPDATE_CREATOR_ROLES: 43,
	MEDIAWORK_TOGGLE_SAMPLE: 44,
	MEDIAWORK_UPDATE: 45,
	MEDIAWORK_MERGE: 46,
	MEDIAWORK_CREATE: 47,
	WORKRELATION_CREATE: 50,
	WORKRELATION_DELETE: 51,
	WORKSOURCE_CREATE: 60,
	WORKSOURCE_UNBIND: 61,
	WORKSOURCE_SET_ORIGIN: 62,
	WORKSOURCE_REFRESH: 63,
	WORKSOURCE_ASSIGN: 64,
	WORKSOURCE_REJECT: 65,
	WORKSOURCE_UPDATE: 66,
	ROLLBACK: 100,

	0: 'Unknown',
	1: 'Tag: Alias',
	2: 'Tag: Unalias',
	3: 'Tag: Delete',
	4: 'Tag: Update',
	5: 'Tag: Set Base',
	6: 'Tag: Add Language',
	7: 'Tag: Edit Wiki',
	8: 'Tag: Edit Connections',
	20: 'Song Attribute: Update',
	21: 'Song: Set Tags',
	22: 'Song Attribute: Alias',
	23: 'Song Attribute: Unalias',
	24: 'Song Attribute: Delete',
	25: 'Song Attribute: Set Base',
	26: 'Song Attribute: Add Language',
	30: 'Song: Create Relation',
	31: 'Song: Delete Relation',
	40: 'Work: Delete',
	41: 'Work: Set Tags',
	42: 'Work: Remove Tag',
	43: 'Work: Update Creator Roles',
	44: 'Work: Toggle Sample',
	45: 'Work: Update',
	46: 'Work: Merge',
	47: 'Work: Create',
	50: 'Work: Create Relation',
	51: 'Work: Delete Relation',
	60: 'Upload: Create',
	61: 'Upload: Unbind',
	62: 'Upload: Set Origin',
	63: 'Upload: Refresh',
	64: 'Upload: Assign',
	65: 'Upload: Reject',
	66: 'Upload: Update',
	100: 'Rollback'
};

export const CommentModelRoutes = {
	mediawork: 'work',
	account: 'profile',
	pool: 'list',
	tagwork: 'tag',
	tagsong: 'song_attribute',
	post: 'post',
	bulkrequest: 'request'
};

export const EntityModelRoutes = {
	...CommentModelRoutes,
	mediasong: 'song',
	worksource: 'upload'
};
