import { browser } from '$app/environment';
import { languages } from '$lib/enums/language';
import { getLocale } from '$lib/paraglide/runtime';
import { unified } from 'unified';
import { WorkTagCategoryMap } from './enums/workTagCategory';
import { m } from './paraglide/messages';
import {
	WorkTagCategory,
	LanguageTypes,
	ThemePref,
	VideoPlatformPref,
	type components,
	GraphViewBackends
} from './schema';
import rehypeStringify from 'rehype-stringify';
import rehypeParse from 'rehype-parse';
import { visit, SKIP } from 'unist-util-visit';
import type { Root, Element, Text } from 'hast';

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
	PREFER_AUTHOR_UPLOAD: false,
	GRAPH_VIEW_BACKEND: GraphViewBackends.Graphviz
};

export const getStoredPrefs = (): Partial<Prefs> =>
	JSON.parse(browser ? (localStorage.getItem('prefs') ?? '{}') : '{}');

export const getLocalPrefs = (): Required<Prefs> => ({
	...defaultPrefs,
	...getStoredPrefs()
});

export const getLocalPref = <T extends keyof Prefs>(setting: T): Required<Prefs>[T] =>
	(getStoredPrefs()[setting] ?? defaultPrefs[setting]) as Required<Prefs>[T];

export const updateLocalPrefs = (values: Partial<Prefs>) => {
	if (!browser) return;
	localStorage.setItem('prefs', JSON.stringify({ ...getStoredPrefs(), ...values }));
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

const splitTrailingPunctuation = (url: string): [string, string] => {
	let end = url.length;
	while (end > 0) {
		const c = url[end - 1];
		if (c === ')') {
			const s = url.slice(0, end);
			if ((s.match(/\)/g)?.length ?? 0) <= (s.match(/\(/g)?.length ?? 0)) break;
		} else if (!/[.,!?;:'"\]}>]/.test(c)) break;
		end--;
	}
	return [url.slice(0, end), url.slice(end)];
};

function rehypeAutolink() {
	return (tree: Root) => {
		visit(tree, (node, index, parent) => {
			if (node.type === 'element' && node.tagName === 'a') return SKIP;
			if (node.type !== 'text' || !parent || index === undefined) return;

			const text = node.value;

			const URL_RE =
				/(?<![\w@/.])(https?:\/\/|www\.)[a-z0-9-]+(\.[a-z0-9-]+)+(:\d+)?([/?#][^\s]*)?/gi;
			if (!URL_RE.test(text)) return;
			URL_RE.lastIndex = 0;

			const children: (Text | Element)[] = [];
			let lastIndex = 0;
			let match;

			while ((match = URL_RE.exec(text))) {
				if (match.index > lastIndex)
					children.push({
						type: 'text',
						value: text.slice(lastIndex, match.index)
					});

				const [url, trailing] = splitTrailingPunctuation(match[0]);

				children.push({
					type: 'element',
					tagName: 'a',
					properties: {
						href: /^https?:\/\//i.test(url) ? url : 'https://' + url,
						target: '_blank',
						rel: ['noopener', 'noreferrer']
					},
					children: [
						{
							type: 'text',
							value: url
						}
					]
				});

				if (trailing) children.push({ type: 'text', value: trailing });

				lastIndex = match.index + match[0].length;
			}

			if (lastIndex < text.length)
				children.push({
					type: 'text',
					value: text.slice(lastIndex)
				});

			parent.children.splice(index, 1, ...children);
			return index + children.length;
		});
	};
}

const autolinkDescriptionProcessor = unified()
	.use(rehypeParse, { fragment: true })
	.use(rehypeAutolink)
	.use(rehypeStringify);

export const autolinkDescription = (description: string) =>
	autolinkDescriptionProcessor.processSync(description).toString();
