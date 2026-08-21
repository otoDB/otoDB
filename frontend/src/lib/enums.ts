import { languages } from '$lib/enums/language.js';
import { mediaConnectionMap } from '$lib/enums/mediaConnection.js';
import { profileConnectionMap } from '$lib/enums/profileConnection.js';
import { songConnectionMap } from '$lib/enums/songConnection.js';
import { TagWorkConnectionMap } from '$lib/enums/tagWorkConnection.js';
import { WorkTagCategoryMap } from '$lib/enums/workTagCategory.js';
import { m } from '$lib/paraglide/messages.js';
import {
	EntityModels,
	HistoricalEntities,
	ModelsWithComments,
	Platform,
	PostEntities,
	Rating,
	SongRelationTypes,
	SongTagCategory,
	Status,
	SubmissionStanding,
	WorkOrigin,
	WorkRelationTypes,
	WorkStatus,
	VideoPlatformPref,
	GraphViewBackends
} from '$lib/schema';

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
	[Status.Delisted]: m.quiet_upper_pig_yell
} as const satisfies Record<Status, () => string>;

export const SubmissionStandingNames = {
	[SubmissionStanding.Pending]: m.such_actual_okapi_dare,
	[SubmissionStanding.Approved]: m.spare_few_kudu_learn,
	[SubmissionStanding.Delisted]: m.quiet_upper_pig_yell,
	[SubmissionStanding.Unbound]: m.fresh_lucky_swan_dwell,
	[SubmissionStanding.Flagged]: m.tangy_busy_liger_burn,
	[SubmissionStanding.Appealed]: m.brief_flat_bullock_dance
} as const satisfies Record<SubmissionStanding, () => string>;

export const WorkOriginNames = {
	[WorkOrigin.Author]: m.crisp_red_canary_tickle,
	[WorkOrigin.Reupload]: m.lucky_still_vulture_work
} as const satisfies Record<WorkOrigin, () => string>;

export const PlatformNames = {
	[Platform.YouTube]: 'YouTube',
	[Platform.Niconico]: 'Niconico',
	[Platform.Bilibili]: 'Bilibili',
	[Platform.SoundCloud]: 'SoundCloud',
	[Platform.Twitter]: 'Twitter',
	[Platform.AcFun]: 'AcFun'
} as const satisfies Record<Platform, string>;

// Auto is preference-only; the rest mirror PlatformNames
export const VideoPlatformPrefNames = {
	[VideoPlatformPref.Auto]: m.brisk_neat_otter_glide,
	...(Object.fromEntries(
		Object.entries(PlatformNames).map(([value, name]) => [value, () => name])
	) as Record<Platform, () => string>)
} satisfies Record<VideoPlatformPref, () => string>;

export const GraphViewBackendNames = {
	[GraphViewBackends.Graphviz]: 'Graphviz',
	[GraphViewBackends.Mermaid]: 'Mermaid'
} satisfies Record<GraphViewBackends, string>;

export const WorkStatusNames = {
	[WorkStatus.Available]: m.this_lime_porpoise_launch,
	[WorkStatus.Down]: m.dizzy_mellow_pug_spur
} as const satisfies Record<WorkStatus, () => string>;

export const MimeType = {
	1: 'image/jpeg',
	2: 'image/png',
	3: 'image/webp'
};

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
	| 'wikipage'
	| 'bulkrequest'
	// This is obvious but we make it explicit
	| EntityModels
	| PostEntities
	| ModelsWithComments
	| HistoricalEntities;

export const EntityModelRoutes: Record<EntityModelType, string> = {
	mediawork: 'work',
	account: 'user',
	pool: 'list',
	tagwork: 'tag',
	tagsong: 'song_attribute',
	post: 'post',
	bulkrequest: 'request',
	mediasong: 'song',
	worksource: 'upload',
	wikipage: 'wiki'
};

export const isValidEntityModelType = (type: string): type is EntityModelType =>
	Object.keys(EntityModelRoutes).includes(type);

export const buildEntityRoutes = (type: EntityModelType, id: string) =>
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
export const enumValues = <E extends Enum<E>>(Enum: E): E[keyof E][] => {
	const Vs = Object.values(Enum);
	return Vs.some((v) => typeof v === 'number')
		? Vs.filter((v) => typeof v === 'number')
		: (Vs as E[keyof E][]);
};
export const isEnum = <E extends Enum<E>>(Enum: E, v: string | number): boolean =>
	enumValues(Enum).includes(v as E[keyof E]);
export const asEnum = <E extends Enum<E>>(Enum: E, v: string | number): E[keyof E] | null =>
	isEnum(Enum, v) ? (v as E[keyof E]) : null;

export type FieldOption = { value: string; label: () => string };

const fromMessages = (r: Record<number, () => string>): FieldOption[] =>
	Object.entries(r).map(([value, label]) => ({ value, label }));
const fromNameFns = (r: Record<number, { nameFn: () => string }>): FieldOption[] =>
	Object.entries(r).map(([value, e]) => ({ value, label: e.nameFn }));
const fromNames = (r: Record<number, { name: string }>): FieldOption[] =>
	Object.entries(r).map(([value, e]) => ({ value, label: () => e.name }));
const fromStrings = (r: Record<number, string>): FieldOption[] =>
	Object.entries(r).map(([value, s]) => ({ value, label: () => s }));

// Each value must appear only once (duplicate values would break <option>),
// so colliding options combine their labels instead
const _mergeOptions = (...lists: FieldOption[][]): FieldOption[] => {
	const byValue = new Map<string, (() => string)[]>();
	for (const o of lists.flat()) {
		const labels = byValue.get(o.value);
		if (labels) labels.push(o.label);
		else byValue.set(o.value, [o.label]);
	}
	return [...byValue.entries()].map(([value, labels]) => ({
		value,
		label: () => [...new Set(labels.map((label) => label()))].join(' / ')
	}));
};

// Disambiguates options merged from models whose enums have similar names
// but different values (e.g. Work vs. Song relations)
const withType = (type: () => string, opts: FieldOption[]): FieldOption[] =>
	opts.map((o) => ({
		...o,
		label: () => m.mild_loud_shad_enchant({ type: type(), name: o.label() })
	}));

// Revision-tracked enum columns -> selectable raw values, merged across the
// models that track a column with that name
export const fieldEnumOptions: Record<string, FieldOption[]> = {
	rating: fromMessages(RatingNames),
	category: _mergeOptions(
		withType(m.empty_legal_chicken_taste, fromNameFns(WorkTagCategoryMap)),
		withType(m.dull_plain_angelfish_cuddle, fromMessages(SongTagCategoryNames))
	),
	relation: _mergeOptions(
		withType(m.grand_merry_fly_succeed, fromMessages(WorkRelationNames)),
		withType(m.grand_nice_pony_belong, fromMessages(SongRelationNames))
	),
	site: _mergeOptions(
		fromNames(TagWorkConnectionMap),
		fromNames(songConnectionMap),
		fromNames(mediaConnectionMap),
		fromNames(profileConnectionMap)
	),
	platform: fromStrings(PlatformNames),
	work_origin: fromMessages(WorkOriginNames),
	work_status: fromMessages(WorkStatusNames),
	thumbnail_mime: fromStrings(MimeType),
	lang: Object.values(languages).map((l) => ({ value: String(l.id), label: () => l.name }))
};
