import { browser } from '$app/environment';
import { LanguageTypes, ThemePref, type components } from './schema';

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

export const GUIDELINE_POST_ID = 4;
export const FAQ_POST_ID = 3;
