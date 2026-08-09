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

const uploader = (id: string, username: string) => ({
	id,
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username
});

const batchSize = 30;

// Production currently serves roughly this many sources, 30 to a page, so the
// list is never short enough to render without a pager.
const totalCount = 34398;

const boundYouTubeSource = {
	added_by: uploader('1', 'Moltern'),
	thumbnail: null,
	media_title: 'Here We Are (In-Game Version) - UNDERTALE',
	platform: Platform.YouTube,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Available,
	url: 'https://www.youtube.com/watch?v=example1',
	work_width: 1920,
	work_height: 1080,
	work_duration: 240,
	title: 'Here We Are (In-Game Version) - UNDERTALE',
	description: null,
	source_id: 'example1',
	uploader_id: 'uploader1',
	is_pending: false,
	media: 100
};

const boundNiconicoSource = {
	added_by: uploader('2', 'tototo'),
	thumbnail: null,
	media_title: '【YTPMV】くるりんパラダイス／ひみつの国',
	platform: Platform.Niconico,
	work_origin: WorkOrigin.Reupload,
	work_status: WorkStatus.Available,
	url: 'https://www.nicovideo.jp/watch/sm0000001',
	work_width: 1280,
	work_height: 720,
	work_duration: 183,
	title: '【YTPMV】くるりんパラダイス／ひみつの国',
	description: null,
	source_id: 'sm0000001',
	uploader_id: 'uploader2',
	is_pending: false,
	media: 101
};

/** Fetched but not yet bound to a work, so the Work column falls back to `-`. */
const unboundSource = {
	added_by: uploader('3', 'Notascryptic'),
	thumbnail: null,
	media_title: null,
	platform: Platform.YouTube,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Available,
	url: 'https://www.youtube.com/watch?v=example2',
	work_width: 1920,
	work_height: 1080,
	work_duration: 95,
	title: 'Life is Roblox - Tate’s Journey',
	description: null,
	source_id: 'example2',
	uploader_id: 'uploader3',
	is_pending: false,
	media: null
};

/**
 * Still awaiting metadata retrieval, so every fetched field is null and the
 * Title column falls back to the raw submitted URL. A query string survives that
 * fallback, so this is the widest string that has no break opportunity.
 */
const unboundPendingSource = {
	added_by: uploader('4', 'Beazty'),
	thumbnail: null,
	media_title: null,
	platform: Platform.Niconico,
	work_origin: WorkOrigin.Reupload,
	work_status: WorkStatus.Available,
	url: 'https://www.nicovideo.jp/watch/sm0000002?ref=search_key_video&playlist=eyJpZCI6IiUyRnNlYXJjaCUyRmV4YW1wbGUiLCJ0eXBlIjoic2VhcmNoIn0',
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

/** The upstream video has gone away. */
const downSource = {
	added_by: uploader('5', 'haruhi'),
	thumbnail: null,
	media_title: 'キーボードクラッシャー「！？」',
	platform: Platform.Twitter,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Down,
	url: 'https://twitter.com/example/status/1234567890',
	work_width: null,
	work_height: null,
	work_duration: null,
	title: null,
	description: null,
	source_id: null,
	uploader_id: null,
	is_pending: false,
	media: 102
};

const templates = [
	boundNiconicoSource,
	boundYouTubeSource,
	boundNiconicoSource,
	unboundSource,
	boundNiconicoSource,
	unboundPendingSource,
	boundYouTubeSource,
	downSource
];

// Fixed anchor, not the current clock, so the stories render the same thing on
// every open and can serve as a regression-test baseline.
const NEWEST_PUBLISHED_DATE = Date.parse('2024-06-05T00:00:00Z');
const DAY = 24 * 60 * 60 * 1000;

/** A full page of sources, as the real list always is. */
const sources = Array.from({ length: batchSize }, (_, i) => ({
	...templates[i % templates.length],
	id: String(i + 1),
	published_date: new Date(NEWEST_PUBLISHED_DATE - i * 37 * DAY).toISOString().slice(0, 10)
}));

// `filters` mirrors the raw search params, so every value is a string or null.
type Filters = { unbound: string | null; pending: string | null; platform: string | null };

const noFilters: Filters = { unbound: null, pending: null, platform: null };

const baseData = {
	user: loggedInUser,
	stats,
	sources: { items: sources, count: totalCount },
	batchSize,
	filters: noFilters,
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

/** The unfiltered list: a full batch of sources with the pager below it. */
export const Default: Story = {};

/** Only a handful of sources are unbound and pending at any one time. */
export const FilteredUnboundPending: Story = {
	args: {
		data: {
			...baseData,
			sources: {
				items: [
					{ ...unboundPendingSource, id: '1', published_date: null },
					{ ...unboundPendingSource, id: '2', published_date: null }
				],
				count: 2
			},
			filters: { unbound: 'true', pending: 'true', platform: null }
		}
	}
};

/**
 * The list itself is never empty, but narrowing the filters far enough that
 * nothing matches is reachable, and that is the only way to see this state.
 */
export const FilteredNoResults: Story = {
	args: {
		data: {
			...baseData,
			sources: { items: [], count: 0 },
			// `filters` mirrors the raw search params, so the platform is a string.
			filters: { unbound: 'true', pending: 'true', platform: String(Platform.Twitter) }
		}
	}
};
