import { browser } from '$app/environment';
import client from '$lib/api';
import { languages } from '$lib/enums/language';
import { setLocale } from '$lib/paraglide/runtime';
import { LanguageTypes, Preferences, ThemePref } from './schema';

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
		await client.POST('/api/profile/pref', {
			fetch,
			body: [
				{
					setting: Preferences.Language,
					value: languages[lang].id
				}
			]
		});
	}
	setLocale(lang);
};

type Prefs = Record<Preferences, number>;

const defaultPrefs: Prefs = {
	[Preferences.Language]: LanguageTypes.en, // reflects baseLocale
	[Preferences.Theme]: ThemePref.Default
};

export const get_prefs = (): Partial<Prefs> | undefined => {
	if (browser) return JSON.parse(localStorage.getItem('prefs') ?? '{}');
};
export const getLocalPref = (setting: Preferences) =>
	get_prefs()?.[setting] ?? defaultPrefs[setting];

export const updateLocalPref = (key: keyof Prefs, value: Prefs[typeof key]) => {
	if (!browser) return;

	localStorage.setItem('prefs', JSON.stringify({ ...get_prefs(), [key]: value }));
};

export const GUIDELINE_POST_ID = 4;
export const FAQ_POST_ID = 3;
