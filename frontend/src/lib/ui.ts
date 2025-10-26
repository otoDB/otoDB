import { browser } from '$app/environment';
import client from './api';
import { Languages, WorkRelationTypes } from './enums';
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

export const mermaid_BFS = (
	ns,
	ls,
	start: number,
	max_distance: number = Number.POSITIVE_INFINITY,
	allowed_types: boolean[] = new Array(WorkRelationTypes.length).fill(true)
) => {
	const nodes = structuredClone(ns),
		links = structuredClone(ls);
	let queue = [[start, 0]];
	while (queue.length) {
		const next_queue = [];
		for (const [n, curr_distance] of queue) {
			const ng = nodes.find((nn) => nn.id === n)!;
			if (curr_distance > max_distance || ng.distance !== undefined) continue;
			ng.distance = curr_distance;
			next_queue.push(
				...[
					...new Set(
						links
							.filter(
								(v) => allowed_types[v.relation] && (v.A_id === n || v.B_id === n)
							)
							.flatMap((v) => [v.A_id, v.B_id])
					)
				].map((nn) => [nn, curr_distance + 1])
			);
		}
		queue = next_queue;
	}
	return [
		nodes.filter((v) => v.distance !== undefined),
		links.filter(
			(v) =>
				allowed_types[v.relation] &&
				nodes.find((w) => w.id === v.A_id).distance !== undefined &&
				nodes.find((w) => w.id === v.B_id).distance !== undefined
		),
		[
			...new Set(
				links
					.filter((v) => allowed_types[v.relation])
					.map((v) => [v.A_id, v.B_id].map((n) => nodes.find((w) => w.id === n)))
					.filter(([a, b]) => (a.distance === undefined) !== (b.distance === undefined))
					.map(([a, b]) => (a.distance !== undefined ? a.id : b.id))
			)
		]
	];
};

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
