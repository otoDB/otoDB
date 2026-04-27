import { PostEntities } from '$lib/schema';
import type { Parent, PhrasingContent, Root } from 'mdast';
import { findAndReplace } from 'mdast-util-find-and-replace';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import rehypeSlug from 'rehype-slug';
import rehypeStringify from 'rehype-stringify';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import { unified, type Plugin } from 'unified';
import { visit } from 'unist-util-visit';

const ENTITIES = [
	{ shortPrefix: 'w', longLabel: 'work', urlPath: 'work' },
	{ shortPrefix: 'l', longLabel: 'list', urlPath: 'list' },
	{ shortPrefix: 'r', longLabel: 'revision', urlPath: 'revision' }
] as const;

const short_prefix_re_gen = (short_prefix: string) =>
	new RegExp(`(?<![/\\w])${short_prefix}(\\d+)(?!\\w)`, 'gi');
const long_label_re_gen = (long_label: string) =>
	new RegExp(`(?<!\\w)${long_label}\\s+#(\\d+)(?!\\w)`, 'gi');
const MENTION_RE = /(?<![\p{L}\p{N}\p{M}_/.])@([\p{L}\p{N}\p{M}_]+)(?![\p{L}\p{N}\p{M}_])/gu;
const TAGWORK_NO_DISPLAY_RE = /\[\[([^\]|]+)\]\]/g;
const TAGWORK_RE = /\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g;
const SEARCH_RE = /\{\{([^}]+?)\}\}/g;

const LinkableEntities: [PostEntities, RegExp][] = [
	[PostEntities.mediawork, short_prefix_re_gen(ENTITIES[0].shortPrefix)],
	[PostEntities.mediawork, long_label_re_gen(ENTITIES[0].longLabel)],
	[PostEntities.account, MENTION_RE],
	[PostEntities.tagwork, TAGWORK_NO_DISPLAY_RE]
];

function link(href: string, text: string): PhrasingContent {
	return { type: 'link', url: href, children: [{ type: 'text', value: text }] };
}

function remarkStripImages() {
	return (tree: Root) => {
		function stripImages(parent: Parent): void {
			for (const child of parent.children) {
				if ('children' in child) {
					stripImages(child as Parent);
				}
			}

			for (let i = 0; i < parent.children.length; ) {
				const node = parent.children[i];
				if (node.type === 'image' || node.type === 'imageReference') {
					parent.children.splice(i, 1);
					continue;
				}
				i++;
			}
		}

		stripImages(tree);
	};
}

const OtodbReplacements: [RegExp, (...args: string[]) => PhrasingContent | false][] = [
	...ENTITIES.flatMap(({ shortPrefix, longLabel, urlPath }) => [
		// Short form: w123, l42, r99
		[
			short_prefix_re_gen(shortPrefix),
			(_, num) => link(`/${urlPath}/${num}`, `${shortPrefix}${num}`)
		] as [RegExp, (...args: string[]) => PhrasingContent | false],
		// Long form: work #123, list #42, revision #99
		[
			long_label_re_gen(longLabel),
			(_, num) => link(`/${urlPath}/${num}`, `${longLabel} #${num}`)
		] as [RegExp, (...args: string[]) => PhrasingContent | false]
	]),
	// Tag wiki links: [[slug]] or [[slug|Display Text]]
	[
		TAGWORK_RE,
		(_, slug, display) =>
			link(`/tag/${encodeURIComponent(slug.trim())}`, display?.trim() || slug.trim())
	],
	// Simple user mention: @username
	[MENTION_RE, (_, username) => link(`/profile/${encodeURIComponent(username)}`, `@${username}`)],
	// Work search: {{tags...}}
	[
		SEARCH_RE,
		(_, query) => ({
			type: 'link',
			url: `/work?tags=${encodeURIComponent(query.trim())}`,
			data: { hProperties: { className: 'otodb-search-link' } },
			children: [{ type: 'text', value: query.trim() }]
		})
	]
];

function remarkOtodb() {
	return (tree: Root) => {
		findAndReplace(tree, OtodbReplacements);
	};
}

export const string_link_entities = (s: string) => {
	let parts: (string | { url: string; text: string })[] = [s];
	for (const [regex, tf] of OtodbReplacements) {
		parts = parts.flatMap((v) => {
			if (typeof v === 'string') {
				const result = [];
				let lastIndex = 0;
				let match;
				while ((match = regex.exec(v)) !== null) {
					if (match.index > lastIndex) result.push(v.slice(lastIndex, match.index));
					const l = tf(...match) as { url: string; children: { value: string }[] };
					result.push({ url: l.url, text: l.children[0].value });
					lastIndex = regex.lastIndex;
				}
				if (lastIndex < v.length) result.push(v.slice(lastIndex));
				return result;
			} else return [v];
		});
	}
	return parts;
};

export const get_entity = (
	s: string
): null | {
	id: string;
	entity: PostEntities;
} => {
	for (const [p, re] of LinkableEntities) {
		const m = s.matchAll(re).next();
		if (m.value)
			return {
				entity: p,
				id: m.value[1]
			};
	}
	return null;
};

const entityShorthands: Record<string, (id: string) => string> = {
	mediawork: (id) => `${ENTITIES[0].shortPrefix}${id}`,
	revision: (id) => `${ENTITIES[2].shortPrefix}${id}`,
	tagwork: (id) => `[[${id}]]`,
	account: (id) => `@${id}`
};

export const entity_to_shorthand = (entity: string, id: string): string =>
	entityShorthands[entity]?.(id) ?? `${entity}/${id}`;

const sanitizeSchema = {
	...defaultSchema,
	tagNames: [...(defaultSchema.tagNames ?? []), 'otodb-worktag'],
	attributes: { ...defaultSchema.attributes, 'otodb-worktag': ['slug'] }
};

const remarkDecodeSimpleLinks: Plugin<[], Root> = () => (tree: Root) => {
	visit(tree, 'link', (node) => {
		if (node.children.length === 1 && node.children[0].type === 'text') {
			const textNode = node.children[0];
			try {
				textNode.value = decodeURIComponent(textNode.value);
			} catch {
				// Ignore
			}
		}
	});
};

const processor = unified()
	.use(remarkParse)
	.use(remarkGfm)
	.use(remarkDecodeSimpleLinks)
	.use(remarkBreaks)
	.use(remarkOtodb)
	.use(remarkStripImages)
	.use(remarkRehype, { allowDangerousHtml: true })
	.use(rehypeRaw)
	.use(rehypeSanitize, sanitizeSchema)
	.use(rehypeSlug)
	.use(rehypeAutolinkHeadings, { behavior: 'wrap' })
	.use(rehypeStringify);

/**
 * Render markdown text to HTML with otoDB extensions.
 */
export const renderMarkdown = (text: string) => String(processor.processSync(text));

/**
 * Extract unique @mentions from markdown source text.
 * Returns list of mentioned usernames.
 */
export const parseMentions = (text: string) => [
	...new Set(text.matchAll(MENTION_RE).map((n) => n[1]))
];
