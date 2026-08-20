import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, Route } from '$lib/schema';
import Page from './+page.svelte';

const handlers = [
	http.post('*/api/history/rollback_user', () => new HttpResponse(null, { status: 200 }))
];

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

const loggedOut = null;

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

const loggedInMod = {
	...loggedInMember,
	username: 'mod_user',
	level: Levels.Mod
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
	},
	batch_size: 30
};

const revisions = {
	items: [
		{
			id: '101',
			date: '2024-06-01T12:00:00Z',
			user: 'member_user',
			index: 0,
			route: Route.Media_Work_Update,
			message: '',
			first_entity: null,
			n_ent: 1
		},
		{
			id: '100',
			date: '2024-05-28T09:30:00Z',
			user: 'member_user',
			index: 0,
			route: Route.Tag_Work_Update,
			message: '',
			first_entity: null,
			n_ent: 3
		},
		{
			id: '99',
			date: '2024-05-20T18:15:00Z',
			user: 'member_user',
			index: 0,
			route: Route.Wiki_Edit,
			message: '',
			first_entity: null,
			n_ent: 1
		}
	],
	count: 3
};

const manyRevisions = {
	items: Array.from({ length: 30 }, (_, i) => ({
		id: `${200 - i}`,
		date: new Date(Date.UTC(2024, 5, 30 - i)).toISOString(),
		user: 'member_user',
		index: 0,
		route: Route.Media_Work_Update,
		message: '',
		first_entity: null,
		n_ent: 1
	})),
	count: 120
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			user: loggedOut,
			revisions
		}
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const LoggedOut: Story = {};

export const MemberViewer: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMember,
			revisions
		}
	}
};

export const ModViewerWithRollback: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMod,
			revisions
		}
	}
};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMember,
			revisions: { items: [], count: 0 }
		}
	}
};

export const Paginated: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMember,
			revisions: manyRevisions
		}
	}
};
