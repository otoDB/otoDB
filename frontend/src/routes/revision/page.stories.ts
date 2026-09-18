import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { HistoricalEntities, Levels, Route, type components } from '$lib/schema';
import Page from './+page.svelte';

type Summary = components['schemas']['RevisionEntitySummarySchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const loggedInUser = {
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

// The load function asks for 20 revisions per page.
const batchSize = 20;

// Production holds far more revisions than one page, so the pager always shows.
const totalCount = 128744;

/**
 * The rows differ in route name length, username length and entity count.
 * The table uses the automatic layout, so these differences move the columns.
 */
const templates: Omit<Summary, 'id' | 'date'>[] = [
	{
		user: 'lo',
		index: 1,
		route: Route.Media_Work_Update,
		message: '',
		first_entity: { id: '10241', entity: HistoricalEntities.mediawork },
		n_ent: 1
	},
	{
		user: 'quiverleaf_archivist',
		index: 1,
		route: Route.Tag_Work_Edit_Connections,
		message: '',
		first_entity: { id: '778', entity: HistoricalEntities.tagwork },
		n_ent: 4
	},
	{
		user: 'mikan',
		index: 2,
		route: Route.Work_Source_Create,
		message: '',
		first_entity: { id: '30022', entity: HistoricalEntities.worksource },
		n_ent: 1
	},
	{
		user: 'brassdoor',
		index: 1,
		route: Route.Song_Tag_Alias_Control,
		message: '',
		first_entity: { id: '4501', entity: HistoricalEntities.tagsong },
		n_ent: 12
	},
	{
		user: 'nn',
		index: 1,
		route: Route.Wiki_Edit,
		message: '',
		first_entity: { id: '61', entity: HistoricalEntities.wikipage },
		n_ent: 1
	},
	{
		user: 'pentaflop_the_third',
		index: 3,
		route: Route.Media_Work_Merge,
		message: '',
		first_entity: { id: '9', entity: HistoricalEntities.mediawork },
		n_ent: 2
	},
	{
		user: 'sable',
		index: 1,
		route: Route.Song_Tag_Set_Tags,
		message: '',
		first_entity: { id: '512', entity: HistoricalEntities.mediasong },
		n_ent: 1
	},
	{
		// A background job writes this revision, and it names no entity.
		user: 'system',
		index: null,
		route: Route.System,
		message: '',
		first_entity: null,
		n_ent: 0
	}
];

// A fixed anchor, not the current clock, keeps every open of the story equal.
const NEWEST_DATE = Date.parse('2024-06-05T09:30:00Z');
const HOUR = 60 * 60 * 1000;

/** A full page of revisions, as the real list always is. */
const revisions: Summary[] = Array.from({ length: batchSize }, (_, i) => ({
	...templates[i % templates.length],
	id: String(totalCount - i),
	date: new Date(NEWEST_DATE - i * 7 * HOUR).toISOString()
}));

/** The rows that the user-and-route filter keeps. */
const wikiEdits: Summary[] = revisions
	.filter((r) => r.route === Route.Wiki_Edit)
	.map((r) => ({ ...r, user: 'quiverleaf_archivist' }));

// Every filter is optional, and the load function drops the empty ones.
const noFilters = {
	username: undefined,
	routes: undefined,
	entity: undefined,
	reason: undefined,
	since: undefined,
	until: undefined,
	is_new: undefined,
	is_deleted: undefined,
	added_tags: undefined,
	removed_tags: undefined,
	changed_tags: undefined,
	changed_field: undefined,
	changed_value: undefined,
	changed_from: undefined
};

const baseData = {
	user: loggedInUser,
	stats,
	results: { items: revisions, count: totalCount },
	filters: noFilters,
	batch_size: batchSize,
	page: 1,
	head: { title: m.giant_away_scallop_hike() }
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** The unfiltered list: a full batch of revisions with the pager below it. */
export const Default: Story = {};

/**
 * A filter on one user and one route. The filter panel opens, and the list
 * shows a short result set, so the columns get different widths.
 */
export const FilteredByUserAndRoute: Story = {
	args: {
		data: {
			...baseData,
			results: { items: wikiEdits, count: wikiEdits.length },
			filters: {
				...noFilters,
				username: 'quiverleaf_archivist',
				routes: [Route.Wiki_Edit]
			}
		}
	}
};

/**
 * The list itself is never empty, but a narrow enough filter matches nothing.
 * That is the only way to see this state.
 */
export const FilteredNoResults: Story = {
	args: {
		data: {
			...baseData,
			results: { items: [], count: 0 },
			filters: {
				...noFilters,
				username: 'quiverleaf_archivist',
				entity: HistoricalEntities.wikipage,
				since: '2024-01-01',
				until: '2024-01-02',
				changed_field: 'title'
			}
		}
	}
};
