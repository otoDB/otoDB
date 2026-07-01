import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { PostCategory } from '$lib/schema';
import Page from './+page.svelte';

const links = [
	{ pathname: 'thread/overview', title: m.just_salty_anaconda_nourish() },
	{ pathname: 'thread/new', title: m.antsy_aloof_horse_grace() },
	{ pathname: 'thread', title: m.mean_top_antelope_love() }
];

const baseData = {
	user: null,
	stats: { works: 1234, tags: 567, songs: 89, lists: 42 },
	head: { title: m.mean_top_antelope_love() },
	links
};

const addedBy = {
	id: '1',
	username: 'member_user',
	level: 1,
	date_created: '2024-01-01T00:00:00Z'
};

const sampleThreads = [
	{
		id: '1',
		added_by: addedBy,
		modified: '2024-06-01T10:00:00Z',
		last_post_by: 'another_user',
		last_post_at: '2024-06-02T10:00:00Z',
		post_count: 12,
		entities: [],
		category: PostCategory.General,
		title: 'A general discussion thread',
		closed_at: null
	},
	{
		id: '2',
		added_by: addedBy,
		modified: '2024-05-20T10:00:00Z',
		last_post_by: null,
		last_post_at: null,
		post_count: 1,
		entities: [],
		category: PostCategory.Bug_Report,
		title: 'Reported a bug in the upload flow',
		closed_at: '2024-05-21T10:00:00Z'
	},
	{
		id: '3',
		added_by: addedBy,
		modified: '2024-06-05T10:00:00Z',
		last_post_by: 'member_user',
		last_post_at: '2024-06-06T10:00:00Z',
		post_count: 34,
		entities: [],
		category: PostCategory.Feature_Request,
		title: 'Feature request: dark mode',
		closed_at: null
	}
];

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			query: '',
			category: null,
			results: { items: sampleThreads, count: sampleThreads.length },
			batch_size: 20
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Default: Story = {};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			query: '',
			category: null,
			results: { items: [], count: 0 },
			batch_size: 20
		}
	}
};

export const SearchResults: Story = {
	args: {
		data: {
			...baseData,
			query: 'dark mode',
			category: null,
			results: { items: [sampleThreads[2]], count: 1 },
			batch_size: 20
		}
	}
};

export const ManyPages: Story = {
	args: {
		data: {
			...baseData,
			query: '',
			category: null,
			results: { items: sampleThreads, count: 120 },
			batch_size: 20
		}
	}
};
