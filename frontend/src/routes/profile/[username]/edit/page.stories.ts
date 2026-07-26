import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, ProfileConnectionTypes } from '$lib/schema';
import Page from './+page.svelte';

const handlers = [http.post('*/api/auth/invite', () => new HttpResponse(null, { status: 200 }))];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const links = [
	{ pathname: 'profile/member_user', title: 'Profile: member_user' },
	{ pathname: 'profile/member_user/lists', title: 'Lists' },
	{ pathname: 'profile/member_user/threads', title: 'Threads' },
	{ pathname: 'profile/member_user/submissions', title: 'Submissions' },
	{ pathname: 'profile/member_user/revisions', title: 'Revisions' },
	{ pathname: 'profile/member_user/edit', title: 'Edit profile' }
];

const head = {
	title: m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: 'member_user' }),
	breadcrumbs: [
		{ name: 'Home', url: '/' },
		{ name: 'member_user', url: '/profile/member_user' }
	]
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
	username: 'editor_user',
	level: Levels.Editor
};

const baseData = {
	stats,
	links,
	head,
	profile: {
		id: '1',
		level: Levels.Member,
		date_created: '2024-01-01T00:00:00Z',
		username: 'member_user'
	}
};

const connections = [
	{ site: ProfileConnectionTypes.Website, content_id: 'https://member-user.example.com' },
	{ site: ProfileConnectionTypes.Twitter, content_id: 'member_user' },
	{ site: ProfileConnectionTypes.YouTube, content_id: '@member_user' }
];

const invites = [
	{
		used_by: {
			id: '2',
			level: Levels.Member,
			date_created: '2024-05-01T00:00:00Z',
			username: 'invited_user'
		},
		used_at: '2024-05-02T00:00:00Z',
		created_at: '2024-04-20T00:00:00Z',
		level: Levels.Member,
		secret: 'invite-secret-used-0001'
	},
	{
		used_by: null,
		used_at: null,
		created_at: '2024-01-01T00:00:00Z',
		level: Levels.Member,
		secret: 'invite-secret-open-0002'
	}
];

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			user: loggedInMember,
			connections: [],
			invites: null
		}
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

// `+page.server.ts` redirects any visitor who is not the profile owner before
// this page ever renders, so `data.user` is always the logged-in owner here.
export const MemberNoConnections: Story = {};

export const MemberWithConnections: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMember,
			connections,
			invites: null
		}
	}
};

export const EditorWithInvites: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInEditor,
			profile: { ...baseData.profile, level: Levels.Editor, username: 'editor_user' },
			connections,
			invites: {
				invites,
				restrictedInvitee: null
			}
		}
	}
};

export const EditorWithRestrictedInvitee: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInEditor,
			profile: { ...baseData.profile, level: Levels.Editor, username: 'editor_user' },
			connections: [],
			invites: {
				invites: [],
				restrictedInvitee: {
					id: '3',
					level: Levels.Member,
					date_created: '2024-06-01T00:00:00Z',
					username: 'restricted_invitee'
				}
			}
		}
	}
};
