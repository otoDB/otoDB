import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import {
	FlagStatus,
	Levels,
	Platform,
	Rating,
	Status,
	WorkOrigin,
	WorkRelationTypes,
	WorkStatus,
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

const addedBy = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

const sources = [
	{
		id: '10',
		added_by: addedBy,
		thumbnail: null,
		media_title: 'Original upload',
		platform: Platform.YouTube,
		work_origin: WorkOrigin.Author,
		work_status: WorkStatus.Available,
		url: 'https://www.youtube.com/watch?v=sample1',
		published_date: '2024-01-05',
		work_width: 1920,
		work_height: 1080,
		work_duration: 245,
		title: 'A sample work title',
		description: 'Check out https://example.com for more information.',
		source_id: null,
		uploader_id: null,
		is_pending: false,
		media: null
	},
	{
		id: '11',
		added_by: addedBy,
		thumbnail: null,
		media_title: 'Reupload',
		platform: Platform.Niconico,
		work_origin: WorkOrigin.Reupload,
		work_status: WorkStatus.Down,
		url: 'https://www.nicovideo.jp/watch/sample2',
		published_date: null,
		work_width: null,
		work_height: null,
		work_duration: null,
		title: null,
		description: null,
		source_id: null,
		uploader_id: null,
		is_pending: true,
		media: null
	}
];

const tags = [
	{
		id: '100',
		lang_prefs: [{ tag: 'サンプル曲', slug: 'sample-song', lang: 2 }],
		aliased_to: null,
		name: 'Sample Song',
		slug: 'sample-song',
		category: WorkTagCategory.Song,
		deprecated: false,
		sample: false,
		creator_roles: null,
		primary_path: []
	},
	{
		id: '101',
		lang_prefs: [],
		aliased_to: null,
		name: 'Sample Creator',
		slug: 'sample-creator',
		category: WorkTagCategory.Creator,
		deprecated: false,
		sample: false,
		creator_roles: [1],
		primary_path: []
	},
	{
		id: '102',
		lang_prefs: [],
		aliased_to: null,
		name: 'Sample Media Source',
		slug: 'sample-media-source',
		category: WorkTagCategory.Media,
		deprecated: false,
		sample: true,
		creator_roles: null,
		primary_path: []
	},
	{
		id: '103',
		lang_prefs: [],
		aliased_to: null,
		name: 'Sample General Tag',
		slug: 'sample-general-tag',
		category: WorkTagCategory.General,
		deprecated: false,
		sample: false,
		creator_roles: null,
		primary_path: []
	}
];

const relatedWork = { id: '2', thumbnail: null, status: Status.Approved, title: 'A related work' };

const relations: [
	{ A_id: string; B_id: string; relation: WorkRelationTypes }[],
	(typeof relatedWork)[]
] = [[{ A_id: '1', B_id: '2', relation: WorkRelationTypes.Sequel }], [relatedWork]];

const comments = [
	{
		id: '200',
		user: addedBy,
		comment: 'This is a top-level comment with some **bold** text.',
		submit_date: '2024-06-01T10:00:00Z',
		parent_id: '0',
		level: 0,
		index: 1,
		edited_at: null,
		edited_by: null
	},
	{
		id: '201',
		user: { ...addedBy, id: '2', username: 'another_user' },
		comment: 'A reply to the first comment.',
		submit_date: '2024-06-01T11:00:00Z',
		parent_id: '200',
		level: 1,
		index: 2,
		edited_at: null,
		edited_by: null
	}
];

const similar = [
	{
		id: '3',
		tags: [],
		thumbnail: null,
		pending_flag: null,
		pending_appeal: null,
		status: Status.Approved,
		title: 'A similar work'
	}
];

const wikiPage = [{ lang: 2, page: 'A sample wiki page in **markdown**.', title: null }];

const baseWork = {
	id: '1',
	thumbnail_source_id: '10',
	tags,
	thumbnail: null,
	pending_flag: null,
	pending_appeal: null,
	relations,
	rating: Rating.General,
	status: Status.Approved,
	wiki_page: wikiPage,
	title: 'A sample work title',
	description: 'A description with an auto-linked URL: https://example.com'
};

const baseData = {
	stats,
	links: loggedOutLinks,
	head,
	sources,
	comments,
	similar
};

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			...baseWork,
			user: guestUser
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Guest: Story = {};

export const Member: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			user: memberUser
		}
	}
};

export const PendingApproval: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			status: Status.Pending,
			user: editorUser
		}
	}
};

export const DelistedWithPendingAppeal: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			status: Status.Delisted,
			pending_appeal: {
				id: '300',
				by: addedBy,
				status: FlagStatus.Value0,
				reason: 'This work was mistakenly delisted.',
				date: '2024-06-10T00:00:00Z'
			},
			user: modUser
		}
	}
};

export const FlaggedForModeration: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			pending_flag: {
				id: '301',
				by: addedBy,
				status: FlagStatus.Value0,
				reason: 'This work needs review.',
				date: '2024-06-11T00:00:00Z'
			},
			user: modUser
		}
	}
};

export const MissingRequiredTags: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			tags: [tags[3]],
			user: memberUser
		}
	}
};

export const NoTagsRelationsOrWiki: Story = {
	args: {
		data: {
			...baseData,
			...baseWork,
			links: loggedInLinks,
			tags: [],
			relations: [[], []] as typeof relations,
			wiki_page: [],
			user: memberUser
		}
	}
};
