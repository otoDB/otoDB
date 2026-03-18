import rehypeRaw from 'rehype-raw';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import rehypeStringify from 'rehype-stringify';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import remarkBreaks from 'remark-breaks';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import remarkGfm from 'remark-gfm';
import { unified } from 'unified';
import { findAndReplace } from 'mdast-util-find-and-replace';
import type { Root, PhrasingContent, Parent } from 'mdast';

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
const LinkableEntities = [
	['mediawork', short_prefix_re_gen(ENTITIES[0].shortPrefix)],
	['mediawork', long_label_re_gen(ENTITIES[0].longLabel)],
	['tagwork', TAGWORK_NO_DISPLAY_RE]
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

function remarkOtodb() {
	return (tree: Root) => {
		const replacements: [RegExp, (...args: string[]) => PhrasingContent | false][] = [];

		for (const { shortPrefix, longLabel, urlPath } of ENTITIES) {
			// Short form: w123, l42, r99
			replacements.push([
				short_prefix_re_gen(shortPrefix),
				(_, num) => link(`/${urlPath}/${num}`, `${shortPrefix}${num}`)
			]);
			// Long form: work #123, list #42, revision #99
			replacements.push([
				long_label_re_gen(longLabel),
				(_, num) => link(`/${urlPath}/${num}`, `${longLabel} #${num}`)
			]);
		}

		// Tag wiki links: [[slug]] or [[slug|Display Text]]
		replacements.push([
			TAGWORK_RE,
			(_, slug, display) =>
				link(`/tag/${encodeURIComponent(slug.trim())}`, display?.trim() || slug.trim())
		]);

		// Simple user mention: @username
		replacements.push([
			MENTION_RE,
			(_, username) => link(`/profile/${encodeURIComponent(username)}`, `@${username}`)
		]);

		findAndReplace(tree, replacements);
	};
}

export const get_entity = (s: string) => {
	for (const [p, re] of LinkableEntities) {
		const m = s.matchAll(re).next();
		if (m.value) return { entity: p, id: m.value[1] };
	}
	return null;
};

const entityShorthands: Record<string, (id: string | number) => string> = {
	mediawork: (id) => `${ENTITIES[0].shortPrefix}${id}`,
	tagwork: (id) => `[[${id}]]`
};

export const entity_to_shorthand = (entity: string, id: string | number): string =>
	entityShorthands[entity]?.(id) ?? `${entity}/${id}`;

const sanitizeSchema = {
	...defaultSchema,
	tagNames: [...(defaultSchema.tagNames ?? []), 'otodb-worktag'],
	attributes: { ...defaultSchema.attributes, 'otodb-worktag': ['slug'] }
};

const processor = unified()
	.use(remarkParse)
	.use(remarkGfm)
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
