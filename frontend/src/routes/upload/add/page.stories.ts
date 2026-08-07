import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { ErrorCode, Levels, WorkStatus } from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

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
	user: loggedInMember,
	stats,
	title: null,
	link: null,
	unavailable_source: null,
	head: {
		title: m.helpful_away_jay_succeed()
	}
};

const unavailableSource = {
	id: '1',
	added_by: {
		id: '1',
		level: Levels.Member,
		date_created: '2024-01-01T00:00:00Z',
		username: 'member_user'
	},
	thumbnail: null,
	media_title: 'Example Unavailable Video',
	platform: 0,
	work_origin: 0,
	work_status: WorkStatus.Down,
	url: 'https://example.com/watch?v=example',
	published_date: '2024-01-01',
	work_width: 1920,
	work_height: 1080,
	work_duration: 180,
	title: 'Example Unavailable Video',
	description: 'A manually described unavailable source.',
	source_id: '1',
	uploader_id: 'uploader_example',
	is_pending: false
};

const meta = {
	component: Page,
	args: {
		data: baseData,
		form: undefined
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const EmptyForm: Story = {};

export const PrefilledUrl: Story = {
	args: {
		data: {
			...baseData,
			link: 'https://example.com/watch?v=example'
		}
	}
};

export const EditingUnavailableSource: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInEditor,
			title: unavailableSource.title,
			unavailable_source: unavailableSource,
			head: {
				title: m.mild_loud_shad_enchant({
					type: m.new_aloof_camel_read(),
					name: unavailableSource.title
				})
			}
		}
	}
};

export const ValidationError: Story = {
	args: {
		data: baseData,
		form: {
			failed: true,
			code: ErrorCode.Bad_Url,
			errorData: {},
			url: 'not-a-valid-url',
			origin: true
		}
	}
};
