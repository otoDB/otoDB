import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, PostCategory, PostEntities } from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const links = [
	{ pathname: 'profile/member_user', title: 'Profile: member_user' },
	{ pathname: 'profile/member_user/lists', title: 'Lists' },
	{ pathname: 'profile/member_user/threads', title: 'Threads' },
	{ pathname: 'profile/member_user/submissions', title: 'Submissions' },
	{ pathname: 'profile/member_user/revisions', title: 'Revisions' }
];

const head = {
	title: m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: 'member_user' }),
	breadcrumbs: [
		{ name: 'Home', url: '/' },
		{ name: 'member_user', url: '/profile/member_user' }
	]
};

const profile = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

const addedBy = {
	id: '1',
	username: 'member_user',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z'
};

const otherUser = {
	id: '2',
	username: 'another_user',
	level: Levels.Member,
	date_created: '2024-02-01T00:00:00Z'
};

const sampleThreads = [
	{
		id: '1',
		added_by: addedBy,
		modified: '2024-06-01T10:00:00Z',
		last_post_by: 'another_user',
		last_post_at: '2024-06-02T10:00:00Z',
		post_count: 12,
		entities: [{ id: 'member_user', entity: PostEntities.account }],
		category: PostCategory.Gardening,
		title: 'A discussion started on my profile',
		closed_at: null
	},
	{
		id: '2',
		added_by: otherUser,
		modified: '2024-05-20T10:00:00Z',
		last_post_by: null,
		last_post_at: null,
		post_count: 1,
		entities: [
			{ id: 'member_user', entity: PostEntities.account },
			{ id: 'example-media-tag', entity: PostEntities.mediawork }
		],
		category: PostCategory.General,
		title: 'A thread also linked to another entity',
		closed_at: '2024-05-21T10:00:00Z'
	}
];

const baseData = {
	user: null,
	stats,
	links,
	head,
	profile,
	batch_size: 20
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			threads: {
				items: sampleThreads,
				count: sampleThreads.length
			}
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Default: Story = {};

export const WithPagination: Story = {
	args: {
		data: {
			...baseData,
			threads: {
				items: sampleThreads,
				count: 45
			}
		}
	}
};
