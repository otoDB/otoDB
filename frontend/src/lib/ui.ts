import { browser } from '$app/environment';
import client from './api';
import { Languages } from './enums';
import { setLocale } from './paraglide/runtime';
import { applyAction, enhance } from '$app/forms';
import { m } from './paraglide/messages';

// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
export const debounce = (callback: Function, wait = 300) => {
	let timeout: ReturnType<typeof setTimeout> | null = null;
	return (...args: any[]) => {
		if (timeout) clearTimeout(timeout);
		timeout = setTimeout(() => callback(...args), wait);
	};
};

export const once = (fn) => {
	return function (event) {
		if (fn) fn.call(this, event);
		fn = null;
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

export const isSVO = (lang: 'en' | 'zh-cn' | 'ko' | 'ja') => lang === 'en' || lang === 'zh-cn';
export const isSOV = (lang: 'en' | 'zh-cn' | 'ko' | 'ja') => lang === 'ko' || lang === 'ja';

export const set_lang = async (lang, logged_in) => {
	if (logged_in) {
		await client.POST('/api/profile/prefs', {
			fetch,
			body: { theme: null, language: Languages[lang] }
		});
	}
	setLocale(lang);
};

interface Prefs {
	theme: string | undefined;
}

export const get_prefs = (): Prefs | undefined => {
	if (browser) return JSON.parse(localStorage.getItem('prefs') ?? '{}');
};

export const update_prefs = (opts: Prefs) => {
	if (browser) localStorage.setItem('prefs', JSON.stringify({ ...get_prefs(), ...opts }));
};

export const isFormDirty = (f: HTMLFormElement) => f.dataset.dirty && !f.action.includes('search');

export const dirtyEnhance = (node: HTMLFormElement) => {
	node.addEventListener('change', () => {
		node.dataset.dirty = 'true';
	});

	return enhance(node, ({ cancel }) => {
		if (Array.from(document.querySelectorAll('form')).some((f) => f !== node && isFormDirty(f)))
			if (!confirm(m.active_lime_panther_buzz())) cancel();
		return async ({ result }) => {
			await applyAction(result);
		};
	});
};

export const version_end_dates = [
	['Pre-Alpha', 1752505560412],
	['Alpha', Number.POSITIVE_INFINITY]
];

export const current_version = version_end_dates.at(-1)[0];
