import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { LanguageTypes, Levels, WikiKind, type components } from '$lib/schema';
import { m } from '$lib/paraglide/messages.js';
import Page from './+page.svelte';

type Row = components['schemas']['WikiIndexRowSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = {
	title: m.mild_loud_shad_enchant({
		type: m.mean_top_antelope_love(),
		name: m.curly_zesty_pelican_aim()
	})
};

const memberUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {
		THEME: 0,
		VIDEO_PLATFORM: 0,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const batch_size = 20;

// The real index holds about 71 pages of 20 rows, so the page always shows a
// full batch with a pager under it.
const total_count = 1413;

const tagRow = (
	slug: string,
	name: string,
	langs: LanguageTypes[],
	lang_prefs: components['schemas']['TagLangPreferenceSchema'][] = []
): Omit<Row, 'last_edited_at'> => ({
	tag: { slug, name, lang_prefs },
	work: null,
	docs: null,
	langs
});

const workRow = (id: number, title: string | null, langs: LanguageTypes[]) => ({
	tag: null,
	work: { id, title },
	docs: null,
	langs
});

const docsRow = (slug: string, title: string | null, langs: LanguageTypes[]) => ({
	tag: null,
	work: null,
	docs: { slug, title },
	langs
});

// One template per row shape the table can render, because `hrefFor` and the
// title cell branch on which reference the row carries. The titles, the slugs
// and the language counts vary a lot on purpose: the column widths come from
// the content of the current page, so the widest and the narrowest cells must
// both appear here.
const templates = [
	// `getTagDisplayName` shows the preference that matches the current locale,
	// so the row needs a preference for the default locale too. Storybook starts
	// at `en`, and without an `en` preference the branch never runs.
	tagRow(
		'invented_character_name',
		'invented_character_name',
		[LanguageTypes.ja],
		[
			{ tag: '架空のキャラクター名', slug: 'kakuu_no_character', lang: LanguageTypes.ja },
			{ tag: 'Invented Character Name', slug: 'invented_character', lang: LanguageTypes.en }
		]
	),
	workRow(4821, 'A Sample Work Title With Several Words In It', [
		LanguageTypes.en,
		LanguageTypes.ja
	]),
	docsRow('sample-style-guide', 'Sample style guide', [LanguageTypes.en]),
	tagRow('short', 'short', [LanguageTypes.en, LanguageTypes.ja, LanguageTypes.ko]),
	// The work has no title, so the cell falls back to `#id`.
	workRow(90210, null, [LanguageTypes.ko]),
	// The underscores give the browser no break opportunity, so this cell is the
	// widest one that cannot wrap. It sets the floor for the title column.
	tagRow(
		'a_sample_tag_slug_that_runs_on_for_a_very_long_time_without_a_break',
		'a_sample_tag_slug_that_runs_on_for_a_very_long_time_without_a_break',
		[LanguageTypes.en, LanguageTypes.ja, LanguageTypes.zh_cn, LanguageTypes.ko]
	),
	docsRow('sample-tagging-rules', 'Sample tagging rules for imaginary source material', [
		LanguageTypes.ja,
		LanguageTypes.zh_cn
	]),
	// The docs page has no title, so the cell falls back to the raw slug. Each
	// hyphen is a break opportunity, so this long cell still wraps.
	docsRow('sample-docs-slug-with-no-title-that-keeps-going-and-going-and-never-breaks', null, [
		LanguageTypes.en
	]),
	workRow(37, 'Short Work', [LanguageTypes.zh_cn]),
	tagRow('another_invented_tag', 'another_invented_tag', [LanguageTypes.en, LanguageTypes.ja])
] satisfies Omit<Row, 'last_edited_at'>[];

// Fixed anchor, not the current clock, so the story renders the same thing on
// every open and can serve as a regression-test baseline.
const NEWEST_EDIT_DATE = Date.parse('2024-06-05T14:32:00Z');
const HOUR = 60 * 60 * 1000;

// A page holds more rows than the templates above, so the extra rows repeat a
// template. Mix the row number into the text of each repeat. Two rows with the
// same text render the same cells, and the table then hides a column width.
const varyRow = (row: Omit<Row, 'last_edited_at'>, n: number): Omit<Row, 'last_edited_at'> => {
	if (row.tag)
		return {
			...row,
			tag: {
				...row.tag,
				slug: `${row.tag.slug}_${n}`,
				name: `${row.tag.name}_${n}`,
				lang_prefs: row.tag.lang_prefs.map((pref) => ({
					...pref,
					tag: `${pref.tag} ${n}`,
					slug: `${pref.slug}_${n}`
				}))
			}
		};
	if (row.work)
		return {
			...row,
			work: {
				...row.work,
				id: row.work.id + n,
				title: row.work.title && `${row.work.title} ${n}`
			}
		};
	if (row.docs)
		return {
			...row,
			docs: {
				...row.docs,
				slug: `${row.docs.slug}-${n}`,
				title: row.docs.title && `${row.docs.title} ${n}`
			}
		};
	return row;
};

const pageOf = (shapes: Omit<Row, 'last_edited_at'>[]): Row[] =>
	Array.from({ length: batch_size }, (_, i) => ({
		...(i < shapes.length ? shapes[i] : varyRow(shapes[i % shapes.length], i + 1)),
		// Every fifth row never got an edit stamp, so the cell shows the dash.
		last_edited_at: i % 5 === 4 ? null : new Date(NEWEST_EDIT_DATE - i * 19 * HOUR).toISOString()
	}));

const items = pageOf(templates);

// The `docs` filter returns wiki pages only, and its first page is as full as
// the unfiltered one.
const docsItems = pageOf(templates.filter((row) => row.docs));

const baseData = {
	stats,
	head,
	user: memberUser,
	q: '',
	kind: '' as WikiKind | '',
	batch_size,
	results: { items, count: total_count }
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** The unfiltered index: a full batch of rows with the pager below the table. */
export const Default: Story = {};

/** The `docs` filter, which keeps only the wiki pages that stand on their own. */
export const FilteredDocs: Story = {
	args: {
		data: {
			...baseData,
			kind: WikiKind.docs,
			results: {
				items: docsItems,
				count: 47
			}
		}
	}
};

/**
 * The index itself is never empty, but a search term that matches nothing is
 * reachable, and that is the only way to see this state.
 */
export const SearchNoResults: Story = {
	args: {
		data: {
			...baseData,
			q: 'a query that matches nothing',
			results: { items: [], count: 0 }
		}
	}
};
