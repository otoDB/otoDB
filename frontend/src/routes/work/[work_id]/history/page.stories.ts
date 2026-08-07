import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels, Rating, Route, Status, WorkRelationTypes, WorkTagCategory } from '$lib/schema';
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
	}
];

const relatedWork = { id: '2', thumbnail: null, status: Status.Approved, title: 'A related work' };

const relations: [
	{ A_id: string; B_id: string; relation: WorkRelationTypes }[],
	(typeof relatedWork)[]
] = [[{ A_id: '1', B_id: '2', relation: WorkRelationTypes.Sequel }], [relatedWork]];

const wikiPage = [{ lang: 2, page: 'A sample wiki page in **markdown**.', title: null }];

// Fields returned by the `work/[work_id]` layout load (`WorkSchema`), which are
// merged into this route's `PageData` alongside `links`/`head` from the same
// layout and `history`/`batch_size` from this page's own load. Unlike the
// sibling `work/[work_id]/page.stories.ts`, `sources`/`comments`/`similar` are
// NOT part of this route's data — those come from the index page's own
// `+page.server.ts`, which is a sibling leaf, not an ancestor layout.
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

const batch_size = 20;

const revisions = [
	{
		id: '400',
		date: '2024-06-12T09:00:00Z',
		user: 'member_user',
		index: 4,
		route: Route.Media_Work_Edit_Wiki,
		message: 'Fixed a typo in the wiki page.'
	},
	{
		id: '300',
		date: '2024-05-01T14:30:00Z',
		user: 'editor_user',
		index: 3,
		route: Route.Media_Work_Update,
		message: 'Updated the title and description.'
	},
	{
		id: '200',
		date: '2024-04-15T08:00:00Z',
		user: 'mod_user',
		index: 2,
		route: Route.Rollback,
		message: 'Rolled back a vandalism edit.'
	},
	{
		id: '100',
		date: '2024-01-01T00:00:00Z',
		user: 'member_user',
		index: 1,
		route: null,
		message: ''
	}
];

const baseData = {
	stats,
	links: loggedOutLinks,
	head,
	...baseWork,
	user: guestUser,
	history: { items: revisions, count: revisions.length },
	batch_size
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Guest: Story = {};

export const MemberWithHistory: Story = {
	args: {
		data: {
			...baseData,
			links: loggedInLinks,
			user: memberUser
		}
	}
};

export const PaginatedHistory: Story = {
	args: {
		data: {
			...baseData,
			links: loggedInLinks,
			user: editorUser,
			history: { items: revisions, count: 145 }
		}
	}
};
