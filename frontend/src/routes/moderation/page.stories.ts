import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import {
	FlagStatus,
	Levels,
	Platform,
	Status,
	WorkOrigin,
	WorkStatus,
	WorkTagCategory
} from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const editorUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'editor_user',
	level: Levels.Editor,
	prefs: {
		THEME: 0,
		VIDEO_PLATFORM: 0,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const links = [
	{ pathname: 'moderation', title: m.direct_fluffy_finch_believe() },
	{ pathname: 'moderation/history', title: m.giant_away_scallop_hike() }
];

const batchSize = 30;

const profile = (id: string, username: string) => ({
	id,
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username
});

const mediaTag = {
	id: '1',
	lang_prefs: [],
	aliased_to: null,
	name: 'Example Media Tag',
	slug: 'example-media-tag',
	category: WorkTagCategory.Media,
	deprecated: false,
	sample: false,
	creator_roles: null
};

const songTag = {
	id: '2',
	lang_prefs: [],
	aliased_to: null,
	name: 'Example Song Tag',
	slug: 'example-song-tag',
	category: WorkTagCategory.Song,
	deprecated: false,
	sample: false,
	creator_roles: null
};

const ordinals = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'];

/** Fixed dates, not the current clock, so every open renders the same thing. */
const flagEvent = (id: string, username: string) => ({
	id,
	by: profile(id, username),
	status: FlagStatus.Value0,
	reason: 'The audio does not match the tagged song.',
	date: '2024-06-05T12:00:00Z'
});

const appealEvent = (id: string, username: string) => ({
	id,
	by: profile(id, username),
	status: FlagStatus.Value0,
	reason: 'The uploader holds the rights to this work.',
	date: '2024-06-04T09:30:00Z'
});

/** A full page of works, as the queue always is. */
const queueWorks = (kind: 'pending' | 'flagged' | 'appealed') =>
	Array.from({ length: batchSize }, (_, i) => ({
		id: String(i + 1),
		tags: i % 3 === 0 ? [] : i % 3 === 1 ? [mediaTag] : [mediaTag, songTag],
		thumbnail: null,
		status: kind === 'appealed' ? Status.Delisted : Status.Pending,
		title: `Example Queued Work ${ordinals[i % ordinals.length]} ${Math.floor(i / ordinals.length) + 1}`,
		pending_flag: kind === 'flagged' ? flagEvent(String(i + 1), 'flagger_user') : null,
		pending_appeal: kind === 'appealed' ? appealEvent(String(i + 1), 'appellant_user') : null
	}));

// Production keeps a few hundred works in the moderation queue, 30 to a page,
// so the list is never short enough to render without a pager.
const queueCount = 418;

const boundSource = {
	added_by: profile('2', 'submitter_one'),
	thumbnail: null,
	media_title: 'Example Bound Work Title',
	platform: Platform.YouTube,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Available,
	url: 'https://www.example-video-host.test/watch?v=example1',
	work_width: 1920,
	work_height: 1080,
	work_duration: 240,
	title: 'Example Submitted Source Title',
	description: null,
	source_id: 'example1',
	uploader_id: 'uploader1',
	is_pending: true,
	media: 100
};

/** Not yet bound to a work, so the Work column falls back to `-`. */
const unboundSource = {
	...boundSource,
	added_by: profile('3', 'submitter_two'),
	media_title: null,
	platform: Platform.Niconico,
	work_origin: WorkOrigin.Reupload,
	url: 'https://www.example-video-share.test/watch/sm0000002',
	title: 'Example Unbound Source Title',
	source_id: 'sm0000002',
	media: null
};

/**
 * Metadata retrieval failed, so the title is null and the Title column falls
 * back to the raw URL. The query string gives the URL no break opportunity,
 * which is the shape that breaks the auto table layout.
 */
const untitledSource = {
	...boundSource,
	added_by: profile('4', 'submitter_three'),
	media_title: null,
	platform: Platform.Twitter,
	url: 'https://www.example-video-host.test/player/embed?video_id=aBcDeFgHiJkL&list=example-playlist-0001&index=42&start=125',
	title: null,
	source_id: null,
	uploader_id: null,
	media: null
};

const sourceTemplates = [boundSource, unboundSource, boundSource, untitledSource, unboundSource];

// Fixed anchor, not the current clock, so the dates never move.
const NEWEST_PUBLISHED_DATE = Date.parse('2024-06-05T00:00:00Z');
const DAY = 24 * 60 * 60 * 1000;

/** A full page of pending sources. */
const sources = Array.from({ length: batchSize }, (_, i) => ({
	...sourceTemplates[i % sourceTemplates.length],
	id: String(i + 1),
	published_date: new Date(NEWEST_PUBLISHED_DATE - i * 11 * DAY).toISOString().slice(0, 10)
}));

// Fewer sources wait for approval than works, but still more than one page.
const sourceCount = 87;

const baseData = {
	user: editorUser,
	stats,
	links,
	head: { title: m.minor_inner_lynx_adapt() },
	batchSize,
	tab: 'all' as const,
	queue: { items: queueWorks('pending'), count: queueCount },
	sources: null
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** The tab that the page opens on: every work that waits for a moderator. */
export const Default: Story = {};

/** Works that a member flagged. Each card gets the flagged outline. */
export const Flagged: Story = {
	args: {
		data: {
			...baseData,
			tab: 'flagged',
			queue: { items: queueWorks('flagged'), count: 62 }
		}
	}
};

/** Works that an uploader appealed after a delist. */
export const Appealed: Story = {
	args: {
		data: {
			...baseData,
			tab: 'appealed',
			queue: { items: queueWorks('appealed'), count: 17 }
		}
	}
};

/**
 * The sources tab, which renders a table instead of a card grid. The fourth
 * row of each group has no title, so the Title cell shows the raw URL.
 */
export const Sources: Story = {
	args: {
		data: {
			...baseData,
			tab: 'sources',
			page: 1,
			queue: null,
			sources: { items: sources, count: sourceCount }
		}
	}
};
