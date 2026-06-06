import { browser } from '$app/environment';
import { page } from '$app/state';
import { languages } from '$lib/enums/language';
import { getLocale } from '$lib/paraglide/runtime';
import { WorkTagCategoryMap } from './enums/workTagCategory';
import { m } from './paraglide/messages';
import {
	WorkTagCategory,
	LanguageTypes,
	ThemePref,
	VideoPlatformPref,
	type components
} from './schema';

export const debounce = <T extends unknown[]>(callback: (...args: T) => void, wait = 300) => {
	let timeout: ReturnType<typeof setTimeout> | null = null;
	return (...args: T) => {
		if (timeout) clearTimeout(timeout);
		timeout = setTimeout(() => callback(...args), wait);
	};
};

export const clickOutside = (node: HTMLElement) => {
	const handleClick = (event: MouseEvent) => {
		if (!node.contains(event.target as Node)) {
			node.dispatchEvent(new CustomEvent('outclick'));
		}
	};

	document.addEventListener('click', handleClick, true);

	return {
		destroy() {
			document.removeEventListener('click', handleClick, true);
		}
	};
};
type Prefs = components['schemas']['UserPreferenceSchema'];

const defaultPrefs: Required<Prefs> = {
	LANGUAGE: LanguageTypes.en, // reflects baseLocale
	THEME: ThemePref.Default,
	VIDEO_PLATFORM: VideoPlatformPref.Auto,
	PREFER_AUTHOR_UPLOAD: false
};

export const getLocalPrefs = (): Partial<Prefs> | undefined => {
	if (browser) return JSON.parse(localStorage.getItem('prefs') ?? '{}');
};

export const getLocalPref = <T extends keyof Prefs>(setting: T): Required<Prefs>[T] =>
	(getLocalPrefs()?.[setting] ?? defaultPrefs[setting]) as Required<Prefs>[T];

export const updateLocalPrefs = (values: Partial<Prefs>) => {
	if (!browser) return;

	localStorage.setItem('prefs', JSON.stringify({ ...getLocalPrefs(), ...values }));
};

export const updateLocalPref = <T extends keyof Prefs>(key: T, value: Prefs[T]) =>
	updateLocalPrefs({ [key]: value } as Partial<Prefs>);

// The server returns unset prefs as null; drop nullish entries so they don't clobber defaults
const definedPrefs = (prefs: Partial<Prefs> | undefined): Partial<Prefs> =>
	Object.fromEntries(Object.entries(prefs ?? {}).filter(([, v]) => v != null)) as Partial<Prefs>;

// Fully-resolved preferences; defaults < local storage < logged-in user
export const getPrefs = (): Required<Prefs> => ({
	...defaultPrefs,
	...definedPrefs(getLocalPrefs()),
	...definedPrefs(page.data?.user?.prefs as Partial<Prefs> | undefined)
});

export const GUIDELINE_POST_ID = '4';
export const FAQ_POST_ID = '3';
export const SEARCH_DOCS_POST_ID = '38';
export const getTagDisplayName = (tag: {
	name: string;
	lang_prefs: { lang: number; tag: string }[];
}) => tag.lang_prefs.find(({ lang }) => lang === languages[getLocale()].id)?.tag ?? tag.name;

export const getTagDisplaySlug = (tag: {
	slug: string;
	lang_prefs: { lang: number; slug: string }[];
}) => tag.lang_prefs.find(({ lang }) => lang === languages[getLocale()].id)?.slug ?? tag.slug;

export function getDisplayText(
	value: string | null | undefined,
	placeholder: string | undefined = undefined
): string {
	return value ?? placeholder ?? m.lost_game_mink_loop();
}

const WORKTAG_REQUIRED_CATEGORIES = [
	WorkTagCategory.Creator,
	WorkTagCategory.Song,
	WorkTagCategory.Source
];
export const getMissingCategories = (
	tags: components['schemas']['TagWorkInstanceThinSchema'][]
) => {
	const present = new Set(
		tags.flatMap((t) =>
			WorkTagCategoryMap[t.category].canSetAsSource && t.sample
				? [WorkTagCategory.Source, t.category]
				: [t.category]
		)
	);
	return WORKTAG_REQUIRED_CATEGORIES.filter((c) => !present.has(c));
};
