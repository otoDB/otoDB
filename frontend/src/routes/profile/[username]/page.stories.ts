import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, ProfileConnectionTypes } from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const linksWithoutEdit = [
	{ pathname: 'profile/member_user', title: 'Profile: member_user' },
	{ pathname: 'profile/member_user/lists', title: 'Lists' },
	{ pathname: 'profile/member_user/threads', title: 'Threads' },
	{ pathname: 'profile/member_user/submissions', title: 'Submissions' },
	{ pathname: 'profile/member_user/revisions', title: 'Revisions' }
];

const linksWithEdit = [
	{ pathname: 'profile/editor_user', title: 'Profile: editor_user' },
	{ pathname: 'profile/editor_user/lists', title: 'Lists' },
	{ pathname: 'profile/editor_user/threads', title: 'Threads' },
	{ pathname: 'profile/editor_user/submissions', title: 'Submissions' },
	{ pathname: 'profile/editor_user/revisions', title: 'Revisions' },
	{ pathname: 'profile/editor_user/edit', title: 'Edit profile' }
];

const head = {
	title: m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: 'member_user' }),
	breadcrumbs: [
		{ name: 'Home', url: '/' },
		{ name: 'member_user', url: '/profile/member_user' }
	]
};

const memberProfile = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

const editorProfile = {
	id: '2',
	level: Levels.Editor,
	date_created: '2023-01-01T00:00:00Z',
	username: 'editor_user'
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

const editorUser = {
	...memberUser,
	user_id: '2',
	username: 'editor_user',
	level: Levels.Editor
};

const modUser = {
	...memberUser,
	user_id: '3',
	username: 'mod_user',
	level: Levels.Mod
};

const connections = [
	{ site: ProfileConnectionTypes.Website, content_id: 'https://member-user.example.com' },
	{ site: ProfileConnectionTypes.Twitter, content_id: 'member_user' },
	{ site: ProfileConnectionTypes.YouTube, content_id: '@member_user' }
];

const comments = [
	{
		id: '200',
		user: memberProfile,
		comment: 'Welcome to your profile! This is a top-level comment with some **bold** text.',
		submit_date: '2024-06-01T10:00:00Z',
		parent_id: '0',
		level: 0,
		index: 1,
		edited_at: null,
		edited_by: null
	},
	{
		id: '201',
		user: { ...memberProfile, id: '4', username: 'another_user' },
		comment: 'A reply to the first comment.',
		submit_date: '2024-06-01T11:00:00Z',
		parent_id: '200',
		level: 1,
		index: 2,
		edited_at: '2024-06-02T09:00:00Z',
		edited_by: { ...memberProfile, id: '4', username: 'another_user' }
	}
];

const baseData = {
	stats,
	links: linksWithoutEdit,
	head,
	profile: memberProfile,
	user: null,
	connections: [],
	comments: []
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const LoggedOutNoConnectionsNoComments: Story = {};

export const MemberViewingWithConnectionsAndComments: Story = {
	args: {
		data: {
			...baseData,
			user: memberUser,
			connections,
			comments
		}
	}
};

export const OwnProfileAsEditor: Story = {
	args: {
		data: {
			...baseData,
			links: linksWithEdit,
			head: {
				title: m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: 'editor_user' }),
				breadcrumbs: [
					{ name: 'Home', url: '/' },
					{ name: 'editor_user', url: '/profile/editor_user' }
				]
			},
			profile: editorProfile,
			user: editorUser,
			connections,
			comments
		}
	}
};

export const ModViewingCanModerateComments: Story = {
	args: {
		data: {
			...baseData,
			user: modUser,
			connections: [],
			comments
		}
	}
};
