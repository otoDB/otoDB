import { m } from '$lib/paraglide/messages.js';

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

export const EntityModelRoutes: Record<EntityModelType, string> = {
	mediawork: 'work',
	account: 'profile',
	pool: 'list',
	tagwork: 'tag',
	tagsong: 'song_attribute',
	post: 'post',
	bulkrequest: 'request',
	mediasong: 'song',
	worksource: 'upload'
};

export const isValidEntityModelType = (type: string): type is EntityModelType =>
	Object.keys(EntityModelRoutes).includes(type);

export const buildEntityRoutes = (type: EntityModelType, id: string | number) =>
	`/${EntityModelRoutes[type]}/${id}`;

export const RequestActions = {
	1: 'worktag:alias',
	2: 'worktag:unalias',
	3: 'worktag:deprecate',
	4: 'worktag:undeprecate',
	5: 'worktag:parent',
	6: 'worktag:unparent'
} as const;

export type Enum<E> = Record<keyof E, number | string> & { [k: number]: string };
export const EnumValues = <E extends Enum<E>>(Enum: E): E[keyof E][] =>
	Object.values(Enum).filter(
		(value) => !(typeof value === 'string' && Enum[value as keyof E] !== undefined)
	) as E[keyof E][];
