import { browser } from '$app/environment';
import client from './api';
import { Languages } from './enums';
import { getLocale, setLocale } from './paraglide/runtime';
import { enhance } from '$app/forms';
import { m } from './paraglide/messages';
import { page } from '$app/state';

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

const dirty_failure = (dirty_forms: HTMLFormElement[], barrier) => {
	dirty_forms.forEach((f) => {
		f.inert = false;
	});
	barrier.forms = undefined;
	barrier.reached = undefined;
};

export const dirtyEnhance = (
	node: HTMLFormElement,
	props:
		| {
				barrier: {
					forms?: HTMLFormElement[];
					reached?: ReturnType<typeof Promise.withResolvers<void>>[];
				};
				pririoty: number;
		  }
		| undefined = undefined
) => {
	node.addEventListener('change', () => {
		node.dataset.dirty = 'true';
		node.dataset.priority = props?.pririoty?.toString();
	});

	return enhance(node, async ({ cancel }) => {
		const dirty_forms = Array.from(document.querySelectorAll('form')).filter(isFormDirty);
		if (props?.barrier) {
			const first = !props?.barrier.reached?.length;
			if (first) {
				if (!dirty_forms.every((f) => f.reportValidity())) {
					cancel();
					return;
				}

				dirty_forms.forEach((f) => {
					f.inert = true;
				});
				props.barrier.forms = dirty_forms.toSorted(
					(a, b) => +a.dataset.priority - +b.dataset.priority
				);
				props.barrier.reached = Array(props.barrier.forms.length)
					.fill(null)
					.map(() => Promise.withResolvers<void>());
			}
			const my_id = props.barrier.forms!.indexOf(node);
			if (first)
				for (let i = 0; i < my_id; i++) {
					props.barrier.forms[i].requestSubmit();
					try {
						await props.barrier.reached[i].promise;
					} catch {
						dirty_failure(dirty_forms, props.barrier);
						break;
					}
				}
			const { resolve, reject } = props.barrier.reached[my_id];

			return async ({ update, result }) => {
				resolve();
				if (result.type === 'success' || result.type === 'redirect') {
					node.dirty = undefined;
					if (first) {
						for (let i = my_id + 1; i < props.barrier.reached?.length; i++) {
							props.barrier.forms[i].requestSubmit();
							try {
								await props.barrier.reached[i].promise;
							} catch {
								dirty_failure(dirty_forms, props.barrier);
								break;
							}
						}
						await update();
					}
				} else {
					reject();
					page.form = result;
				}
			};
		} else if (dirty_forms.some((f) => f !== node) && !confirm(m.active_lime_panther_buzz()))
			cancel();
	});
};

export const version_end_dates = [
	['Pre-Alpha', 1752505560412],
	['Alpha', 1766984874569],
	['Beta', Number.POSITIVE_INFINITY]
];

export const current_version = version_end_dates.at(-1)![0];

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
