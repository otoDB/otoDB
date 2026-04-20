import { browser } from '$app/environment';
import client from '$lib/api';
import { languages } from '$lib/enums/language';
import { setLocale } from '$lib/paraglide/runtime';
import type { ThemePref } from './schema';

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
				theme: null,
				language: languages[lang].id
			}
		});
	}
	setLocale(lang);
};

interface Prefs {
	theme?: ThemePref; // theme id
}

const getLocalPrefs = (): Prefs => {
	if (!browser) return {};

	return JSON.parse(localStorage.getItem('prefs') ?? '{}');
};
export const getLocalTheme = () => getLocalPrefs()?.theme;

export const updateLocalPref = (key: keyof Prefs, value: Prefs[typeof key]) => {
	if (!browser) return;

	localStorage.setItem('prefs', JSON.stringify({ ...getLocalPrefs(), [key]: value }));
};
export const updateLocalTheme = (themeId: ThemePref) => updateLocalPref('theme', themeId);

export const GUIDELINE_POST_ID = 4;
export const FAQ_POST_ID = 3;
