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

export const allMediaTypeKeys = Object.keys(MediaType).filter((e) => !isNaN(+e));

export const RequestActions = {
	1: 'worktag:alias',
	2: 'worktag:unalias',
	3: 'worktag:deprecate',
	4: 'worktag:undeprecate',
	5: 'worktag:parent',
	6: 'worktag:unparent'
} as const;

export const PostCategories = [
	m.livid_loose_eel_pop,
	m.crazy_loud_trout_peek,
	m.new_honest_tapir_endure,
	m.moving_trick_piranha_thrive,
	m.fresh_lower_rook_trip
];

/**
 * @deprecated
 */
export const CommentModelRoutes = {
	mediawork: 'work',
	account: 'profile',
	pool: 'list',
	tagwork: 'tag',
	tagsong: 'song_attribute',
	post: 'post',
	bulkrequest: 'request'
};

/**
 * @deprecated
 */
export const EntityModelRoutes = {
	...CommentModelRoutes,
	mediasong: 'song',
	worksource: 'upload'
};

export type EntityModelType =
	| 'post'
	| 'mediasong'
	| 'worksource'
	| 'mediawork'
	| 'account'
	| 'pool'
	| 'tagwork'
	| 'tagsong'
	| 'bulkrequest';

export const isValidEntityModelType = (type: string): type is EntityModelType =>
	Object.keys(EntityModelRoutes).includes(type);

export const buildEntityRoutes = (type: EntityModelType, id: string | number) =>
	`/${EntityModelRoutes[type]}/${id}`;

export const ErrorCode = {
	LOGIN_FAILED: 10000,
	NOT_LOGGED_IN: 10001,
	USERNAME_TAKEN: 10002,
	VALIDATION_ERROR: 10003,
	EDITOR_ONLY: 10004,
	BAD_URL: 10005,
	SOURCE_HAS_WORK: 10006,
	NO_MATCHING_ENTITIES: 10007,
	NAME_SLUG_MISMATCH: 10008
} as const;
