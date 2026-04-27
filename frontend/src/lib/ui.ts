import { browser } from '$app/environment';
import client from '$lib/api';
import { languages } from '$lib/enums/language';
import { getLocale, setLocale } from '$lib/paraglide/runtime';
import { WorkTagCategoryMap } from './enums/workTagCategory';
import { m } from './paraglide/messages';
import { WorkTagCategory, LanguageTypes, ThemePref, type components } from './schema';

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
			node.dispatchEvent(new CustomEvent('Outclick'));
		}
	};

	document.addEventListener('click', handleClick, true);

	return {
		destroy() {
			document.removeEventListener('click', handleClick, true);
		}
	};
};
export const set_lang = async (lang: keyof typeof languages, logged_in: boolean) => {
	if (logged_in) {
		await client.POST('/api/profile/prefs', {
			fetch,
			body: {
				LANGUAGE: languages[lang].id
			}
		});
	}
	setLocale(lang);
};

type Prefs = components['schemas']['UserPreferenceSchema'];

const defaultPrefs: Prefs = {
	LANGUAGE: LanguageTypes.en, // reflects baseLocale
	THEME: ThemePref.Default
};

export const getLocalPrefs = (): Partial<Prefs> | undefined => {
	if (browser) return JSON.parse(localStorage.getItem('prefs') ?? '{}');
};

export const getLocalPref = <T extends keyof Prefs>(setting: T): Prefs[T] =>
	getLocalPrefs()?.[setting] ?? defaultPrefs[setting];

export const updateLocalPref = <T extends keyof Prefs>(key: T, value: Prefs[T]) => {
	if (!browser) return;

	localStorage.setItem('prefs', JSON.stringify({ ...getLocalPrefs(), [key]: value }));
};

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
	WorkTagCategory.Source,
	WorkTagCategory.General
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
