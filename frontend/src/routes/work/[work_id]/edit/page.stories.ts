import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import {
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

const handlers = [http.get('*/api/wiki/page', () => HttpResponse.json([]))];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const links = [
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

const relatedWork = { id: '2', thumbnail: null, status: Status.Approved, title: 'A related work' };

const relations: [
	{ A_id: string; B_id: string; relation: WorkRelationTypes }[],
	(typeof relatedWork)[]
] = [[{ A_id: '1', B_id: '2', relation: WorkRelationTypes.Sequel }], [relatedWork]];

const wikiPage = [{ lang: 2, page: 'A sample wiki page in **markdown**.', title: null }];

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

const baseData = {
	stats,
	links,
	head,
	sources,
	tags,
	id: '1',
	thumbnail_source_id: '10',
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

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			user: memberUser
		},
		form: undefined
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Member: Story = {};

export const Editor: Story = {
	args: {
		data: {
			...baseData,
			user: editorUser
		},
		form: undefined
	}
};

export const ModCanDelete: Story = {
	args: {
		data: {
			...baseData,
			user: modUser
		},
		form: undefined
	}
};

export const PendingWorkAllowsOriginEdit: Story = {
	args: {
		data: {
			...baseData,
			status: Status.Pending,
			user: memberUser
		},
		form: undefined
	}
};

export const NoWikiOrRelations: Story = {
	args: {
		data: {
			...baseData,
			wiki_page: [],
			relations: [[], []] as typeof relations,
			user: memberUser
		},
		form: undefined
	}
};

export const WithFormError: Story = {
	args: {
		data: {
			...baseData,
			user: memberUser
		},
		form: {
			failed: true,
			code: -1,
			errorData: {},
			title: 'An edited title',
			description: 'An edited description',
			rating: String(Rating.General),
			thumbnail_source_id: '10',
			reason: 'Fixing typo'
		}
	}
};
