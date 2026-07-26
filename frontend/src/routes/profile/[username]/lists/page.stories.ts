import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels } from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const ownerLinks = [
	{ pathname: 'profile/member_user', title: 'Profile: member_user' },
	{ pathname: 'profile/member_user/lists', title: 'Lists' },
	{ pathname: 'profile/member_user/threads', title: 'Threads' },
	{ pathname: 'profile/member_user/submissions', title: 'Submissions' },
	{ pathname: 'profile/member_user/revisions', title: 'Revisions' },
	{ pathname: 'profile/member_user/edit', title: 'Edit profile' }
];

const visitorLinks = [
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

const baseData = {
	stats,
	head,
	profile
};

const loggedInMember = {
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

const loggedInEditor = {
	...loggedInMember,
	level: Levels.Editor
};

const viewerUser = {
	...loggedInMember,
	user_id: '2',
	username: 'viewer_user'
};

const sampleLists = [
	{
		id: '1',
		author: profile,
		upstream: null,
		name: "member_user's Favorite Songs",
		description: 'A curated collection of favorite songs.'
	},
	{
		id: '2',
		author: profile,
		upstream: 'https://example.com/original-list',
		name: 'Imported Playlist',
		description: null
	},
	{
		id: '3',
		author: profile,
		upstream: null,
		name: 'Untitled List',
		description: null
	}
];

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			links: ownerLinks,
			user: loggedInMember,
			lists: []
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const OwnProfileEmpty: Story = {};

export const OwnProfileWithLists: Story = {
	args: {
		data: {
			...baseData,
			links: ownerLinks,
			user: loggedInMember,
			lists: sampleLists
		}
	}
};

export const OwnProfileEditorWithLists: Story = {
	args: {
		data: {
			...baseData,
			links: ownerLinks,
			user: loggedInEditor,
			lists: sampleLists
		}
	}
};

export const OtherUsersProfile: Story = {
	args: {
		data: {
			...baseData,
			links: visitorLinks,
			user: viewerUser,
			lists: sampleLists
		}
	}
};

export const LoggedOutVisitor: Story = {
	args: {
		data: {
			...baseData,
			links: visitorLinks,
			user: null,
			lists: sampleLists
		}
	}
};
