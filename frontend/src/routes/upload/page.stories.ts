import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, Platform, WorkOrigin, WorkStatus } from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const loggedInUser = {
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

const addedBy = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

const boundSource = {
	id: '1',
	added_by: addedBy,
	thumbnail: null,
	media_title: 'Example Work',
	platform: Platform.YouTube,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Available,
	url: 'https://www.youtube.com/watch?v=example1',
	published_date: '2024-05-01',
	work_width: 1920,
	work_height: 1080,
	work_duration: 240,
	title: 'Example Uploaded Video',
	description: null,
	source_id: 'example1',
	uploader_id: 'uploader1',
	is_pending: false,
	media: 100
};

const unboundPendingSource = {
	id: '2',
	added_by: addedBy,
	thumbnail: null,
	media_title: null,
	platform: Platform.Niconico,
	work_origin: WorkOrigin.Reupload,
	work_status: WorkStatus.Available,
	url: 'https://www.nicovideo.jp/watch/sm0000002',
	published_date: '2024-06-15',
	work_width: null,
	work_height: null,
	work_duration: null,
	title: null,
	description: null,
	source_id: null,
	uploader_id: null,
	is_pending: true,
	media: null
};

const downSource = {
	id: '3',
	added_by: addedBy,
	thumbnail: null,
	media_title: null,
	platform: Platform.Twitter,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Down,
	url: 'https://twitter.com/example/status/1234567890',
	published_date: null,
	work_width: null,
	work_height: null,
	work_duration: null,
	title: null,
	description: null,
	source_id: null,
	uploader_id: null,
	is_pending: false,
	media: null
};

const baseData = {
	user: loggedInUser,
	stats,
	sources: { items: [boundSource, unboundPendingSource, downSource], count: 3 },
	batchSize: 30,
	filters: { unbound: null, pending: null, platform: null },
	head: { title: m.extra_brave_tapir_skip() }
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Populated: Story = {};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			sources: { items: [], count: 0 }
		}
	}
};

export const FilteredUnboundPending: Story = {
	args: {
		data: {
			...baseData,
			sources: { items: [unboundPendingSource], count: 1 },
			filters: { unbound: 'true', pending: 'true', platform: null }
		}
	}
};

export const ManyPages: Story = {
	args: {
		data: {
			...baseData,
			sources: { items: [boundSource, unboundPendingSource, downSource], count: 250 }
		}
	}
};
