import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, Platform, Status, SubmissionStanding, WorkOrigin, WorkStatus } from '$lib/schema';
import Page from './+page.svelte';

const handlers = [http.post('*/api/upload/refresh', () => HttpResponse.json({}))];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const links = [
	{ pathname: 'user/member_user', title: 'Profile: member_user' },
	{ pathname: 'user/member_user/lists', title: 'Lists' },
	{ pathname: 'user/member_user/threads', title: 'Threads' },
	{ pathname: 'user/member_user/submissions', title: 'Submissions' },
	{ pathname: 'user/member_user/revisions', title: 'Revisions' },
	{ pathname: 'user/member_user/edit', title: 'Edit profile' }
];

const head = {
	title: m.mild_loud_shad_enchant({ type: m.fuzzy_crazy_cobra_lead(), name: 'member_user' }),
	breadcrumbs: [
		{ name: 'Home', url: '/' },
		{ name: 'member_user', url: '/user/member_user' }
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
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
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
	profile,
	batch_size: 30,
	order: null,
	origin: null,
	platform: null,
	status: null,
	dir: ''
};

const pendingSubmissions = {
	items: [
		{
			id: '1',
			added_by: addedBy,
			thumbnail: null,
			media_title: 'Example Uploaded Work',
			platform: Platform.YouTube,
			work_origin: WorkOrigin.Author,
			work_status: WorkStatus.Available,
			url: 'https://www.youtube.com/watch?v=example1',
			published_date: '2024-03-01',
			work_width: 1920,
			work_height: 1080,
			work_duration: 240,
			title: 'Example Uploaded Work',
			description: null,
			source_id: 'example1',
			uploader_id: null,
			is_pending: true,
			media: null,
			media_status: null
		},
		{
			id: '2',
			added_by: addedBy,
			thumbnail: null,
			media_title: null,
			platform: Platform.Niconico,
			work_origin: WorkOrigin.Reupload,
			work_status: WorkStatus.Available,
			url: 'https://www.nicovideo.jp/watch/example2',
			published_date: '2024-02-15',
			work_width: null,
			work_height: null,
			work_duration: null,
			title: null,
			description: null,
			source_id: 'example2',
			uploader_id: null,
			is_pending: true,
			media: null,
			media_status: null
		}
	],
	count: 2
};

const approvedSubmissions = {
	items: [
		{
			id: '3',
			added_by: addedBy,
			thumbnail: null,
			media_title: 'Approved Work',
			platform: Platform.YouTube,
			work_origin: WorkOrigin.Author,
			work_status: WorkStatus.Available,
			url: 'https://www.youtube.com/watch?v=example3',
			published_date: '2024-01-10',
			work_width: 1920,
			work_height: 1080,
			work_duration: 180,
			title: 'Approved Work',
			description: null,
			source_id: 'example3',
			uploader_id: null,
			is_pending: false,
			media: '100',
			media_status: Status.Approved
		}
	],
	count: 1
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			user: null,
			standing: SubmissionStanding.Pending,
			submissions: pendingSubmissions
		}
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const PendingAsGuest: Story = {};

export const PendingAsOwner: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMember,
			standing: SubmissionStanding.Pending,
			submissions: pendingSubmissions
		}
	}
};

export const PendingAsEditor: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInEditor,
			standing: SubmissionStanding.Pending,
			submissions: pendingSubmissions
		}
	}
};

export const Approved: Story = {
	args: {
		data: {
			...baseData,
			user: null,
			standing: SubmissionStanding.Approved,
			submissions: approvedSubmissions
		}
	}
};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			user: null,
			standing: SubmissionStanding.Pending,
			submissions: { items: [], count: 0 }
		}
	}
};
