import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import {
	FlagStatus,
	Levels,
	ModerationAction,
	ModerationEventType,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type ModerationEvent = components['schemas']['ModerationEventSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = { title: m.minor_inner_lynx_adapt() };

const links = [{ pathname: 'moderation/history', title: m.giant_away_scallop_hike() }];

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

// `schema.ts` names these enum members after their numbers, so the story gives
// each member the label that `ModerationEventsTable` renders for it.
const EventType = {
	Flagged: ModerationEventType.Value0,
	Appealed: ModerationEventType.Value1,
	Rejected: ModerationEventType.Value2,
	Approved: ModerationEventType.Value3,
	ModerationAction: ModerationEventType.Value4
};

const Action = {
	Delisted: ModerationAction.Value1,
	UploadApproved: ModerationAction.Value10,
	UploadRejected: ModerationAction.Value11
};

const moderator = (id: string, username: string) => ({ id, username });

const batchSize = 30;

// The moderation log grows with every report and every action, so the real page
// is always a full batch with a pager below it.
const totalCount = 8642;

// One template per label that `ModerationEventsTable` can render: the five event
// types, and the three moderation actions that event type 4 splits into. The
// templates also cover every target shape (work, source, both, neither), a null
// moderator, an empty reason, and a long reason that holds a pasted URL. The
// long reason is the content that the `max-w-xs truncate` cell hides today.
const templates = [
	{
		event_type: EventType.Flagged,
		work_id: '4821',
		source_id: null,
		by: moderator('11', 'kz'),
		reason: 'The audio track does not match the work that the entry names.',
		status: FlagStatus.Value0
	},
	{
		event_type: EventType.Appealed,
		work_id: '4821',
		source_id: null,
		by: moderator('12', 'quietharbor'),
		reason: 'The uploader states that the mismatch comes from a stale thumbnail.',
		status: FlagStatus.Value1
	},
	{
		event_type: EventType.Rejected,
		work_id: null,
		source_id: '90312',
		by: moderator('13', 'longwinded_moderator_handle'),
		reason:
			'The report repeats an earlier report about the same source, so this one closes without a separate action. The earlier discussion is at https://example.invalid/moderation/threads/2f8c1d4b-report-about-a-duplicate-source?highlight=true and it holds the full history. Please read that thread before you file the same report again.',
		status: FlagStatus.Value2
	},
	{
		event_type: EventType.Approved,
		work_id: '5507',
		source_id: null,
		by: moderator('14', 'nix'),
		reason: '',
		status: FlagStatus.Value1
	},
	{
		event_type: EventType.ModerationAction,
		work_id: '5507',
		source_id: '90344',
		by: moderator('15', 'sunlit_meridian_curator'),
		reason: 'The rights holder asked for the removal of this work.',
		status: Action.Delisted
	},
	{
		event_type: EventType.ModerationAction,
		work_id: null,
		source_id: '90355',
		by: moderator('16', 'pw'),
		reason: 'The metadata matches the linked video.',
		status: Action.UploadApproved
	},
	{
		event_type: EventType.ModerationAction,
		work_id: null,
		source_id: '90361',
		by: null,
		reason: 'The upstream video is private, so the automatic check rejected the upload.',
		status: Action.UploadRejected
	},
	{
		event_type: EventType.Flagged,
		work_id: null,
		source_id: null,
		by: moderator('17', 'threefold_lantern'),
		reason: 'A general report about the tag guidelines, with no work or source attached.',
		status: FlagStatus.Value0
	}
] satisfies Omit<ModerationEvent, 'event_id' | 'event_at'>[];

// Fixed anchor, not the current clock, so the stories render the same thing on
// every open and can serve as a regression-test baseline.
const NEWEST_EVENT_AT = Date.parse('2024-06-05T14:32:00Z');
const HOUR = 60 * 60 * 1000;

/** A full page of events, as the real log always is. */
const events: ModerationEvent[] = Array.from({ length: batchSize }, (_, i) => ({
	...templates[i % templates.length],
	event_id: `event-${i + 1}`,
	event_at: new Date(NEWEST_EVENT_AT - i * 3 * HOUR).toISOString()
}));

const baseData = {
	user: memberUser,
	stats,
	links,
	head,
	events: { items: events, count: totalCount },
	batchSize,
	userId: undefined
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** The whole log: a full batch of events with the pager below the table. */
export const Default: Story = {};

/** One moderator alone accounts for far fewer events, so the pager drops away. */
export const FilteredByModerator: Story = {
	args: {
		data: {
			...baseData,
			events: {
				items: events.filter((event) => event.by?.id === '15').slice(0, 4),
				count: 4
			},
			userId: '15'
		}
	}
};

/**
 * The log itself is never empty, but a filter on a moderator who took no action
 * matches nothing, and that is the only way to reach this state.
 */
export const FilteredNoResults: Story = {
	args: {
		data: {
			...baseData,
			events: { items: [], count: 0 },
			userId: '99'
		}
	}
};
