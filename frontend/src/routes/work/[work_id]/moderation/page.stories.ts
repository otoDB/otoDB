import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import {
	FlagStatus,
	Levels,
	ModerationAction,
	ModerationEventType,
	Rating,
	Status,
	WorkTagCategory
} from '$lib/schema';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const loggedOutLinks = [
	{ pathname: 'work/1', title: 'Work #1' },
	{ pathname: 'work/1/threads', title: 'Threads' },
	{ pathname: 'work/1/history', title: 'History' },
	{ pathname: 'work/1/moderation', title: 'Moderation' }
];

const loggedInLinks = [
	{ pathname: 'work/1', title: 'Work #1' },
	{ pathname: 'work/1/tags', title: 'Tags' },
	{ pathname: 'work/1/relations', title: 'Relations' },
	{ pathname: 'work/1/edit', title: 'Edit' },
	{ pathname: 'work/1/threads', title: 'Threads' },
	{ pathname: 'work/1/history', title: 'History' },
	{ pathname: 'work/1/moderation', title: 'Moderation' }
];

const head = {
	title: 'A sample work title',
	image: null,
	isExplicit: false,
	breadcrumbs: [
		{ name: 'Home', url: '/' },
		{ name: 'Works', url: '/work' },
		{ name: 'A sample work title', url: '/work/1' }
	]
};

const guestUser = null;

const memberUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const modUser = {
	...memberUser,
	user_id: '3',
	username: 'mod_user',
	level: Levels.Mod
};

const eventAuthor = { id: '1', username: 'member_user' };
const modAuthor = { id: '3', username: 'mod_user' };

const tags = [
	{
		id: '100',
		lang_prefs: [],
		aliased_to: null,
		name: 'Sample Song',
		slug: 'sample-song',
		category: WorkTagCategory.Song,
		deprecated: false,
		sample: false,
		creator_roles: null,
		primary_path: []
	}
];

type RelatedWorkSummary = { id: string; thumbnail: string | null; status: Status; title: string };

const baseWork = {
	id: '1',
	thumbnail_source_id: '10',
	tags,
	thumbnail: null,
	pending_flag: null,
	pending_appeal: null,
	relations: [[], []] as [{ A_id: string; B_id: string; relation: number }[], RelatedWorkSummary[]],
	rating: Rating.General,
	status: Status.Approved,
	wiki_page: [],
	title: 'A sample work title',
	description: 'A description with an auto-linked URL: https://example.com'
};

const baseData = {
	stats,
	links: loggedOutLinks,
	head
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			...baseWork,
			user: guestUser,
			events: { items: [], count: 0 }
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Empty: Story = {};

export const WithEvents: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			user: modUser,
			events: {
				items: [
					{
						event_id: '1',
						event_type: ModerationEventType.Value0,
						work_id: '1',
						source_id: null,
						by: eventAuthor,
						reason: 'Flagged for review by a member.',
						status: FlagStatus.Value0,
						event_at: '2024-06-01T10:00:00Z'
					},
					{
						event_id: '2',
						event_type: ModerationEventType.Value1,
						work_id: '1',
						source_id: null,
						by: modAuthor,
						reason: 'Delisted pending investigation.',
						status: FlagStatus.Value1,
						event_at: '2024-06-02T09:00:00Z'
					},
					{
						event_id: '3',
						event_type: ModerationEventType.Value4,
						work_id: '1',
						source_id: null,
						by: modAuthor,
						reason: 'Approved after review.',
						status: ModerationAction.Value1,
						event_at: '2024-06-03T12:30:00Z'
					},
					{
						event_id: '4',
						event_type: ModerationEventType.Value4,
						work_id: null,
						source_id: '10',
						by: modAuthor,
						reason: 'Source unbound from work.',
						status: ModerationAction.Value10,
						event_at: '2024-06-04T15:00:00Z'
					},
					{
						event_id: '5',
						event_type: ModerationEventType.Value4,
						work_id: '1',
						source_id: null,
						by: null,
						reason: 'Automatically re-checked by the system.',
						status: ModerationAction.Value11,
						event_at: '2024-06-05T00:00:00Z'
					}
				],
				count: 5
			}
		}
	}
};

export const MemberView: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			user: memberUser,
			events: { items: [], count: 0 }
		}
	}
};
