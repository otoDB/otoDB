import { m } from '$lib/paraglide/messages.js';
import {
	Platform,
	Rating,
	SongRelationTypes,
	SongTagCategory,
	Status,
	WorkOrigin,
	WorkRelationTypes,
	WorkStatus
} from './schema';

export const SongTagCategoryNames = {
	[SongTagCategory.General]: m.fresh_lower_rook_trip,
	[SongTagCategory.Genre]: m.cozy_awful_mule_enrich,
	[SongTagCategory.Author]: m.crisp_red_canary_tickle,
	[SongTagCategory.Meta]: m.sad_next_jaguar_renew
} as const satisfies Record<SongTagCategory, () => string>;

export const RatingNames = {
	[Rating.General]: m.fresh_lower_rook_trip,
	[Rating.Sensitive]: m.sound_such_sloth_talk,
	[Rating.Explicit]: m.mad_sound_walrus_tap
} as const satisfies Record<Rating, () => string>;

export const StatusNames = {
	[Status.Pending]: m.such_actual_okapi_dare,
	[Status.Approved]: m.spare_few_kudu_learn,
	[Status.Unapproved]: m.stale_vexed_hare_pray
} as const satisfies Record<Status, () => string>;

export const WorkOriginNames = {
	[WorkOrigin.Author]: m.crisp_red_canary_tickle,
	[WorkOrigin.Reupload]: m.lucky_still_vulture_work
} as const satisfies Record<WorkOrigin, () => string>;

export const WorkStatusNames = {
	[WorkStatus.Available]: m.this_lime_porpoise_launch,
	[WorkStatus.Down]: m.dizzy_mellow_pug_spur
} as const satisfies Record<WorkStatus, () => string>;

export const MimeType = {
	1: 'image/jpeg',
	2: 'image/png',
	3: 'image/webp'
};

export const PlatformNames = {
	[Platform.YouTube]: 'YouTube',
	[Platform.Niconico]: 'Niconico',
	[Platform.Bilibili]: 'Bilibili',
	[Platform.SoundCloud]: 'SoundCloud',
	[Platform.Twitter]: 'Twitter',
	[Platform.AcFun]: 'AcFun'
} as const satisfies Record<Platform, string>;

export const WorkRelationNames = {
	[WorkRelationTypes.Sequel]: m.spry_muddy_sloth_radiate,
	[WorkRelationTypes.Respect]: m.inclusive_just_rabbit_succeed,
	[WorkRelationTypes.Collab_Part]: m.full_gaudy_sloth_value,
	[WorkRelationTypes.Sample]: m.icy_raw_gazelle_heal
} as const satisfies Record<WorkRelationTypes, () => string>;

export const WorkRelationEditorPredicate = {
	[WorkRelationTypes.Sequel]: m.curly_many_orangutan_grip,
	[WorkRelationTypes.Respect]: m.sound_funny_hound_embrace,
	[WorkRelationTypes.Collab_Part]: m.shy_bland_bird_harbor,
	[WorkRelationTypes.Sample]: m.major_tense_fly_savor
} as const satisfies Record<WorkRelationTypes, () => string>;

export const WorkRelationDisplayForward = {
	[WorkRelationTypes.Sequel]: m.free_mellow_tiger_cook,
	[WorkRelationTypes.Respect]: m.dizzy_true_florian_pop,
	[WorkRelationTypes.Collab_Part]: m.safe_gray_cowfish_dart,
	[WorkRelationTypes.Sample]: m.icy_raw_gazelle_heal
} as const satisfies Record<WorkRelationTypes, () => string>;

export const WorkRelationDisplayBackward = {
	[WorkRelationTypes.Sequel]: m.spry_muddy_sloth_radiate,
	[WorkRelationTypes.Respect]: m.simple_fair_mallard_roar,
	[WorkRelationTypes.Collab_Part]: m.full_gaudy_sloth_value,
	[WorkRelationTypes.Sample]: m.lazy_awful_gopher_build
} as const satisfies Record<WorkRelationTypes, () => string>;

export const SongRelationNames = {
	[SongRelationTypes.Remix]: m.antsy_north_reindeer_radiate,
	[SongRelationTypes.Remaster]: m.bold_polite_myna_delight,
	[SongRelationTypes.Medley]: m.light_caring_deer_coax,
	[SongRelationTypes.Sequel]: m.spry_muddy_sloth_radiate
} as const satisfies Record<SongRelationTypes, () => string>;

export const SongRelationPredicate = {
	[SongRelationTypes.Remix]: m.frail_nimble_tadpole_arrive,
	[SongRelationTypes.Remaster]: m.mellow_only_bulldog_arise,
	[SongRelationTypes.Medley]: m.giant_petty_shad_exhale,
	[SongRelationTypes.Sequel]: m.curly_many_orangutan_grip
} as const satisfies Record<SongRelationTypes, () => string>;

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
