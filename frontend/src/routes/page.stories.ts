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

const makeWorks = (prefix: string, titles: string[]) =>
	titles.map((title, i) => ({
		id: `${prefix}-${i + 1}`,
		title,
		thumbnail: null,
		status: Status.Approved,
		tags: []
	}));

const sampleRandomWorks = makeWorks('random', [
	'A wonderful song',
	'Another great work',
	'A third piece',
	'A fourth composition',
	'A fifth arrangement',
	'A sixth remix'
]);

const sampleRecentWorks = makeWorks('recent', [
	'Freshly uploaded track',
	'Newly added work',
	'Just submitted piece',
	'Latest upload',
	'Recently registered song',
	'Brand new entry'
]);

const changeRoutes = [
	{
		route: Route.Media_Work_Update,
		first_entity: { id: '1', entity: HistoricalEntities.mediawork, label: 'Freshly uploaded track' }
	},
	{
		route: Route.Tag_Work_Update,
		first_entity: {
			id: 'touhou_project',
			entity: HistoricalEntities.tagwork,
			label: 'touhou_project'
		}
	},
	{
		route: Route.Song_Tag_Update,
		first_entity: { id: 'remix', entity: HistoricalEntities.tagsong, label: 'remix' }
	},
	{
		route: Route.Media_Work_Set_Tags,
		first_entity: { id: '4', entity: HistoricalEntities.mediawork, label: null }
	},
	{
		route: Route.Work_Source_Update,
		first_entity: { id: '5', entity: HistoricalEntities.worksource, label: 'Latest upload' }
	},
	{
		route: Route.Wiki_Edit,
		first_entity: { id: 'about', entity: HistoricalEntities.wikipage, label: 'about' }
	},
	{
		route: Route.Tag_Work_Alias,
		first_entity: { id: 'kirby', entity: HistoricalEntities.tagwork, label: 'kirby' }
	},
	{
		route: Route.Media_Work_Merge,
		first_entity: { id: '8', entity: HistoricalEntities.mediawork, label: 'Brand new entry' }
	}
];

const sampleChanges = {
	items: changeRoutes.map(({ route, first_entity }, i) => ({
		id: `${i + 1}`,
		date: `2024-06-${String(8 - i).padStart(2, '0')}T10:00:00Z`,
		user: i % 2 === 0 ? 'member_user' : 'another_user',
		index: 1,
		route,
		message: '',
		first_entity,
		n_ent: (i % 3) + 1
	})),
	count: 8
};

const postCategories = [
	PostCategory.General,
	PostCategory.Bug_Report,
	PostCategory.Feature_Request,
	PostCategory.Announcement,
	PostCategory.Gardening,
	PostCategory.General,
	PostCategory.Bug_Report,
	PostCategory.Feature_Request
];

const postTitles = [
	'A general discussion thread',
	'Reported a bug in the upload flow',
	'Feature request: dark mode',
	'Upcoming maintenance announcement',
	'Cleaning up duplicate tags',
	'Question about tag aliases',
	'Cannot upload large files',
	'Suggestion: bulk tag editing'
];

const samplePosts = {
	items: postCategories.map((category, i) => ({
		id: `${i + 1}`,
		added_by: addedBy,
		modified: `2024-06-${String(8 - i).padStart(2, '0')}T10:00:00Z`,
		last_post_by: i % 4 === 3 ? null : 'another_user',
		last_post_at: i % 4 === 3 ? null : `2024-06-${String(8 - i).padStart(2, '0')}T12:00:00Z`,
		post_count: (i + 1) * 3,
		entities: [],
		category,
		title: postTitles[i],
		closed_at: i % 4 === 3 ? '2024-06-09T10:00:00Z' : null
	})),
	count: 8
};

const baseData = {
	user: null,
	stats,
	random: sampleRandomWorks,
	recent: sampleRecentWorks,
	changes: sampleChanges,
	posts: samplePosts,
	head: {
		title: m.glad_born_mouse_taste(),
		description: m.mild_loud_shad_enchant({
			type: 'otoDB',
			name: m.glad_born_mouse_taste()
		}),
		image: 'https://otodb.net/thumb.png'
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
