import { browser } from '$app/environment';
import client from '$lib/api';
import { languages } from '$lib/enums/language';
import { getLocale, setLocale } from '$lib/paraglide/runtime';
import { m } from '$lib/paraglide/messages';

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
	theme?: number; // theme id
}

export const get_prefs = (): Prefs | undefined => {
	if (browser) return JSON.parse(localStorage.getItem('prefs') ?? '{}');
};
export const getLocalTheme = () => get_prefs()?.theme;

export const updateLocalPref = (key: keyof Prefs, value: Prefs[typeof key]) => {
	if (!browser) return;

	localStorage.setItem('prefs', JSON.stringify({ ...get_prefs(), [key]: value }));
};
export const updateLocalTheme = (themeId: number) => updateLocalPref('theme', themeId);

export const GUIDELINE_POST_ID = 4;
export const FAQ_POST_ID = 3;

const MINUTE = 60;
const HOUR = MINUTE * 60;
const DAY = HOUR * 24;
const WEEK = DAY * 7;
const MONTH = DAY * 30;
const YEAR = DAY * 365;

// prettier-ignore
export function timeAgo(date: string | Date): string {
	const d = date instanceof Date ? date : new Date(date);
	const diff = (d.getTime() - Date.now()) / 1000;
	const elapsed = Math.abs(diff);

	if (elapsed <= 1) return m.busy_hour_bee_gasp();

	const rtf = new Intl.RelativeTimeFormat(getLocale(), { numeric: 'always' });

	const [divisor, unit]: [number, Intl.RelativeTimeFormatUnit] =
		elapsed > YEAR   * 2 ? [YEAR,   'year']   :
		elapsed > MONTH  * 2 ? [MONTH,  'month']  :
		elapsed > WEEK   * 2 ? [WEEK,   'week']   :
		elapsed > DAY    * 2 ? [DAY,    'day']    :
		elapsed > HOUR   * 2 ? [HOUR,   'hour']   :
		elapsed > MINUTE * 2 ? [MINUTE, 'minute'] :
		                       [1,      'second'] ;

	return rtf.format(Math.trunc(diff / divisor), unit);
}
