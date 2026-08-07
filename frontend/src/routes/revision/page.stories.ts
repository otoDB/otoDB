import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { HistoricalEntities, Route } from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const emptyFilters = {
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

const changeRoutes = [
	{ route: Route.Media_Work_Update, entity: HistoricalEntities.mediawork },
	{ route: Route.Tag_Work_Update, entity: HistoricalEntities.tagwork },
	{ route: Route.Song_Tag_Update, entity: HistoricalEntities.tagsong },
	{ route: Route.Media_Work_Set_Tags, entity: HistoricalEntities.mediawork },
	{ route: Route.Work_Source_Update, entity: HistoricalEntities.worksource },
	{ route: Route.Wiki_Edit, entity: HistoricalEntities.wikipage }
];

const sampleItems = changeRoutes.map(({ route, entity }, i) => ({
	id: `${i + 1}`,
	date: `2024-06-${String(8 - i).padStart(2, '0')}T10:00:00Z`,
	user: i % 2 === 0 ? 'member_user' : 'another_user',
	index: 1,
	route,
	message: '',
	first_entity: { id: `${i + 1}`, entity },
	n_ent: (i % 3) + 1
}));

// A rollback entry with no resolvable entity (e.g. the entity was later
// removed), exercising the branch where `first_entity` is null.
const rollbackItem = {
	id: '100',
	date: '2024-05-01T09:00:00Z',
	user: 'editor_user',
	index: 2,
	route: Route.Rollback,
	message: 'Reverted vandalism',
	first_entity: null,
	n_ent: 0
};

const baseData = {
	user: null,
	stats,
	filters: emptyFilters,
	batch_size: 20,
	page: 1,
	head: { title: m.giant_away_scallop_hike() }
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			results: { items: [...sampleItems, rollbackItem], count: 145 }
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Populated: Story = {};

export const WithPagination: Story = {
	args: {
		data: {
			...baseData,
			page: 3,
			results: { items: sampleItems, count: 145 }
		}
	}
};

export const WithFiltersApplied: Story = {
	args: {
		data: {
			...baseData,
			filters: {
				username: 'member_user',
				routes: [Route.Media_Work_Update, Route.Tag_Work_Update],
				entity: HistoricalEntities.mediawork,
				reason: 'cleanup',
				since: '2024-01-01',
				until: '2024-06-30',
				is_new: true,
				is_deleted: false,
				added_tags: ['example-tag-a', 'example-tag-b'],
				removed_tags: ['example-tag-c'],
				changed_tags: ['example-tag-d'],
				changed_field: 'rating',
				changed_value: undefined,
				changed_from: undefined
			},
			results: { items: sampleItems, count: sampleItems.length }
		}
	}
};
