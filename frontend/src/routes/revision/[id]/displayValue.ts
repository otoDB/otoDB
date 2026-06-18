import {
	MimeType,
	PlatformNames,
	RatingNames,
	SongRelationNames,
	SongTagCategoryNames,
	WorkOriginNames,
	WorkRelationNames,
	WorkStatusNames,
	type Enum
} from '$lib/enums.js';
import { creatorRole, resolveCreatorRoleKeyById } from '$lib/enums/creatorRole.js';
import { languages, resolveLanguageKeyById } from '$lib/enums/language.js';
import { mediaConnectionMap } from '$lib/enums/mediaConnection.js';
import { mediaTypes, resolveMediaTypeKeyById } from '$lib/enums/mediaType.js';
import { profileConnectionMap } from '$lib/enums/profileConnection.js';
import { songConnectionMap } from '$lib/enums/songConnection.js';
import { TagWorkConnectionMap } from '$lib/enums/tagWorkConnection.js';
import { WorkTagCategoryMap } from '$lib/enums/workTagCategory.js';
import { m } from '$lib/paraglide/messages';

type DisplayFunction = () => string;
const EnumMap_to_DisplayFunction =
	<E extends Enum<E>>(fs: Record<E[keyof E], { name: string }>) =>
	(v: number): DisplayFunction =>
	() =>
		fs[v as E[keyof E]].name;
const EnumValues_to_DisplayFunction =
	<E extends Enum<E>>(fs: Record<E[keyof E], { nameFn: DisplayFunction }>) =>
	(v: number): DisplayFunction =>
		fs[v as E[keyof E]].nameFn;
const Values_to_DisplayFunction =
	(r: (b: number) => string, fs: Record<string, { nameFn: DisplayFunction }>) =>
	(v: number): DisplayFunction =>
		fs[r(v)].nameFn;
const StraightValues_to_DisplayFunction =
	(r: (b: number) => string, fs: Record<string, { name: string }>) =>
	(v: number): DisplayFunction =>
	() =>
		fs[r(v)].name;
const EnumStraightRecord_to_DisplayFunction =
	<E extends Enum<E>>(fs: Record<E[keyof E], string>) =>
	(v: number): DisplayFunction =>
	() =>
		fs[v as E[keyof E]];
const StraightRecord_to_DisplayFunction =
	<T extends number>(r: Record<T, string>) =>
	(v: number): DisplayFunction =>
	() =>
		r[v as T];
const EnumRecord_to_DisplayFunction =
	<E extends Enum<E>>(fs: Record<E[keyof E], DisplayFunction>) =>
	(v: number): DisplayFunction =>
		fs[v as E[keyof E]];
const expand_bit_field =
	(r: (b: number) => string, fs: Record<string, { nameFn: DisplayFunction }>) =>
	(v: number): DisplayFunction =>
	() =>
		[...v.toString(2)]
			.reduce(
				(a, e, i, aa) =>
					e === '1' ? [...a, Values_to_DisplayFunction(r, fs)(1 << (aa.length - 1 - i))()] : a,
				[] as string[]
			)
			.join(', ') || 'N/A';

const Languages = StraightValues_to_DisplayFunction(resolveLanguageKeyById, languages);

const ValueDisplayMap: Record<string, Record<string, (v: number) => DisplayFunction>> = {
	mediawork: {
		rating: EnumRecord_to_DisplayFunction(RatingNames)
	},
	tagwork: {
		category: EnumValues_to_DisplayFunction(WorkTagCategoryMap),
		media_type: expand_bit_field(resolveMediaTypeKeyById, mediaTypes)
	},
	tagsong: {
		category: EnumRecord_to_DisplayFunction(SongTagCategoryNames)
	},
	tagworkconnection: {
		site: EnumMap_to_DisplayFunction(TagWorkConnectionMap)
	},
	mediasongconnection: {
		site: EnumMap_to_DisplayFunction(songConnectionMap)
	},
	tagworkmediaconnection: {
		site: EnumMap_to_DisplayFunction(mediaConnectionMap)
	},
	tagworkcreatorconnection: {
		site: EnumMap_to_DisplayFunction(profileConnectionMap)
	},
	tagworklangpreference: {
		lang: Languages
	},
	tagsonglangpreference: {
		lang: Languages
	},
	workrelation: {
		relation: EnumRecord_to_DisplayFunction(WorkRelationNames)
	},
	songrelation: {
		relation: EnumRecord_to_DisplayFunction(SongRelationNames)
	},
	tagworkinstance: {
		creator_roles: expand_bit_field(resolveCreatorRoleKeyById, creatorRole)
	},
	wikipage: {
		lang: Languages
	},
	worksource: {
		platform: EnumStraightRecord_to_DisplayFunction(PlatformNames),
		thumbnail_mime: StraightRecord_to_DisplayFunction(MimeType),
		work_origin: EnumRecord_to_DisplayFunction(WorkOriginNames),
		work_status: EnumRecord_to_DisplayFunction(WorkStatusNames)
	}
};

export const hasDisplayHandler = (type: string, col: string | null | undefined) =>
	col != null && ValueDisplayMap[type]?.[col] !== undefined;

export const displayValue = (
	type: keyof typeof ValueDisplayMap,
	col: string,
	val: string | null | undefined
) => {
	if (val === null || val === undefined) return m.pale_blunt_moth_lack();
	const handler = ValueDisplayMap[type]?.[col];
	if (!handler) return val;
	try {
		return handler(+val)();
	} catch {
		// Historic values may no longer exist in the current enum maps
		return val;
	}
};
