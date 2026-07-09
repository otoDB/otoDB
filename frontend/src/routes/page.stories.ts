import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import {
	HistoricalEntities,
	Levels,
	PostCategory,
	Route,
	Status,
	ThemePref,
	VideoPlatformPref
} from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const addedBy = {
	id: '1',
	username: 'member_user',
	level: 1,
	date_created: '2024-01-01T00:00:00Z'
};

const sampleWorks = [
	{
		id: '1',
		title: 'A wonderful song',
		thumbnail: null,
		status: Status.Approved,
		tags: []
	},
	{
		id: '2',
		title: 'Another great work',
		thumbnail: null,
		status: Status.Approved,
		tags: []
	},
	{
		id: '3',
		title: 'A third piece',
		thumbnail: null,
		status: Status.Approved,
		tags: []
	}
];

const sampleChanges = {
	items: [
		{
			id: '1',
			date: '2024-06-01T10:00:00Z',
			user: 'member_user',
			index: 1,
			route: Route.Media_Work_Update,
			message: '',
			first_entity: { id: '1', entity: HistoricalEntities.mediawork },
			n_ent: 1
		},
		{
			id: '2',
			date: '2024-05-30T10:00:00Z',
			user: 'another_user',
			index: 1,
			route: Route.Tag_Work_Update,
			message: '',
			first_entity: { id: '2', entity: HistoricalEntities.tagwork },
			n_ent: 2
		}
	],
	count: 2
};

const samplePosts = {
	items: [
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
		}
	],
	count: 2
};

const baseData = {
	user: null,
	stats,
	random: sampleWorks,
	recent: sampleWorks,
	changes: sampleChanges,
	posts: samplePosts,
	head: {
		title: m.glad_born_mouse_taste(),
		description: m.mild_loud_shad_enchant({
			type: 'otoDB',
			name: m.glad_born_mouse_taste()
		})
	}
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Guest: Story = {};

export const LoggedIn: Story = {
	args: {
		data: {
			...baseData,
			user: {
				csrf: 'csrf-token',
				user_id: '1',
				username: 'member_user',
				level: Levels.Member,
				prefs: {
					THEME: ThemePref.Plain_Light,
					VIDEO_PLATFORM: VideoPlatformPref.Auto,
					PREFER_AUTHOR_UPLOAD: false
				},
				notifs_count: 0,
				notifs_nonsub_count: 0
			}
		}
	}
};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			random: [],
			recent: [],
			changes: { items: [], count: 0 },
			posts: { items: [], count: 0 }
		}
	}
};
