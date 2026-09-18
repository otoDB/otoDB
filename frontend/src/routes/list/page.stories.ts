import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, type components } from '$lib/schema';
import Page from './+page.svelte';

type List = components['schemas']['ListSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 54 };

const head = {
	title: m.mild_loud_shad_enchant({
		type: m.mean_top_antelope_love(),
		name: m.stale_loose_squid_cut()
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

// Production holds this many lists, 20 to a page, so the page always shows a
// full batch and a pager.
const total_count = 54;

const author = (id: string, username: string) => ({
	id,
	username,
	level: Levels.Member,
	date_created: '2023-01-15T09:00:00Z'
});

// `name` is arbitrary user text. The templates cover the shapes that the column
// must hold: short names, long names with spaces, non-Latin names, and one name
// that is a single run of characters with no break opportunity. The last one is
// what pushes the table past the section, so the layout fix needs to see it.
const templates = [
	{
		author: author('1', 'member_user'),
		upstream: null,
		name: 'Favourite uploads of 2024',
		description: 'A short list of the uploads that I replay the most.'
	},
	{
		author: author('2', 'editor_user'),
		upstream: null,
		name: 'お気に入りの音MAD',
		description: null
	},
	{
		author: author('3', 'archivist_user'),
		upstream: 'https://example.com/playlists/1',
		name: 'A considerably longer list name that wraps onto several lines, so the column can be checked against realistic text rather than a single short phrase',
		description: 'Imported from an external playlist.'
	},
	{
		author: author('4', 'a_notably_long_account_name_user'),
		upstream: null,
		name: 'ThisListNameIsOneVeryLongRunOfCharactersWithNoWhitespaceOrHyphenAnywhereInItSoTheBrowserFindsNoBreakOpportunityAtAll',
		description: null
	},
	{
		author: author('5', 'mod_user'),
		upstream: null,
		name: 'Reference tracks',
		description: null
	}
] satisfies Omit<List, 'id'>[];

const lists: List[] = Array.from({ length: batch_size }, (_, i) => ({
	...templates[i % templates.length],
	id: String(i + 1)
}));

const baseData = {
	user: memberUser,
	stats,
	head,
	query: '',
	results: { items: lists, count: total_count },
	batch_size
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** A full batch of `batch_size` lists with the pager below the table. */
export const Default: Story = {};

/** A query that matches only part of the collection. */
export const WithQuery: Story = {
	args: {
		data: {
			...baseData,
			query: 'reference',
			results: { items: [{ ...templates[4], id: '5' }], count: 1 }
		}
	}
};

/**
 * The collection itself is never empty, but a query that matches nothing is
 * reachable, and that is the only way to see this state.
 */
export const QueryWithNoResults: Story = {
	args: {
		data: {
			...baseData,
			query: 'a query that matches nothing',
			results: { items: [], count: 0 }
		}
	}
};
