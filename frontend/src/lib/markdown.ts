import rehypeStringify from 'rehype-stringify';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import { unified } from 'unified';
import { findAndReplace } from 'mdast-util-find-and-replace';
import type { Root, PhrasingContent } from 'mdast';

const ENTITIES = [
	{ shortPrefix: 'w', longLabel: 'work', urlPath: 'work' },
	{ shortPrefix: 'l', longLabel: 'list', urlPath: 'list' },
	{ shortPrefix: 'r', longLabel: 'revision', urlPath: 'revision' }
] as const;

const MENTION_RE = /(?<![\p{L}\p{N}\p{M}_/.])@([\p{L}\p{N}\p{M}_]+)(?![\p{L}\p{N}\p{M}_])/gu;

function link(href: string, text: string): PhrasingContent {
	return { type: 'link', url: href, children: [{ type: 'text', value: text }] };
}

function remarkOtodb() {
	return (tree: Root) => {
		const replacements: [RegExp, (...args: string[]) => PhrasingContent | false][] = [];

		for (const { shortPrefix, longLabel, urlPath } of ENTITIES) {
			// Short form: w123, l42, r99
			replacements.push([
				new RegExp(`(?<![/\\w])${shortPrefix}(\\d+)(?!\\w)`, 'gi'),
				(_, num) => link(`/${urlPath}/${num}`, `${shortPrefix}${num}`)
			]);
			// Long form: work #123, list #42, revision #99
			replacements.push([
				new RegExp(`(?<!\\w)${longLabel}\\s+#(\\d+)(?!\\w)`, 'gi'),
				(_, num) => link(`/${urlPath}/${num}`, `${longLabel} #${num}`)
			]);
		}

		// Tag wiki links: [[slug]] or [[slug|Display Text]]
		replacements.push([
			/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g,
			(_, slug, display) =>
				link(`/tag/${encodeURIComponent(slug.trim())}`, display?.trim() || slug.trim())
		]);

		// Simple user mention: @username
		replacements.push([
			new RegExp(MENTION_RE.source, 'gu'),
			(_, username) => link(`/profile/${encodeURIComponent(username)}`, `@${username}`)
		]);

		findAndReplace(tree, replacements);
	};
}

const processor = unified()
	.use(remarkParse)
	.use(remarkGfm)
	.use(remarkBreaks)
	.use(remarkOtodb)
	.use(remarkRehype)
	.use(rehypeStringify);

/**
 * Render markdown text to HTML with otoDB extensions.
 */
export function renderMarkdown(text: string): string {
	return String(processor.processSync(text));
}

/**
 * Extract unique @mentions from markdown source text.
 * Returns sorted list of mentioned usernames.
 */
export function parseMentions(text: string): string[] {
	const names = new Set<string>();
	for (const match of text.matchAll(new RegExp(MENTION_RE.source, 'gu'))) {
		names.add(match[1]);
	}
	return [...names].sort();
}
