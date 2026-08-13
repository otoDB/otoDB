import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import {
	ErrorCode,
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

// `GuidelineWarning` calls `/api/wiki/page` on mount. The other handlers cover
// the buttons and the origin select in the source table.
const handlers = [
	http.get('*/api/wiki/page', () => HttpResponse.json([])),
	http.put('*/api/upload/origin', () => HttpResponse.json({})),
	http.post('*/api/upload/refresh', () => HttpResponse.json({}))
];

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

// The source table is the widest element on this page. Keep a long title, a
// long description and a source whose title is null, because that source falls
// back to the raw URL with its query string.
const sources = [
	{
		// `baseWork.thumbnail_source_id` points at this source, so its thumbnail
		// also fills the preview below the thumbnail select. Storybook serves the
		// image from `.storybook/static`.
		id: '10',
		added_by: addedBy,
		thumbnail: '/storybook-static/thumbnail_1280x720.jpg',
		media_title: 'Original upload',
		platform: Platform.YouTube,
		work_origin: WorkOrigin.Author,
		work_status: WorkStatus.Available,
		url: 'https://www.youtube.com/watch?v=sample1',
		published_date: '2024-01-05',
		work_width: 1920,
		work_height: 1080,
		work_duration: 245,
		title: 'A sample work title with a fairly long name that does not wrap',
		description:
			'A sample description.\nIt has several lines.\nSee https://example.com/sample for more information.',
		source_id: 'sample1',
		uploader_id: 'sample-author',
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
		work_status: WorkStatus.Available,
		url: 'https://www.nicovideo.jp/watch/sample2',
		published_date: '2023-11-20',
		work_width: 1280,
		work_height: 720,
		work_duration: 248,
		title: 'A sample reupload title',
		description: 'A short sample description for the reupload.',
		source_id: 'sample2',
		uploader_id: null,
		is_pending: false,
		media: null
	},
	{
		// This source has no title, so the table shows the raw URL instead. The
		// query string makes the cell very wide. The source also has no published
		// date, so the date cell stays empty.
		id: '12',
		added_by: addedBy,
		thumbnail: null,
		media_title: null,
		platform: Platform.Bilibili,
		work_origin: WorkOrigin.Reupload,
		work_status: WorkStatus.Available,
		url: 'https://www.bilibili.com/video/SAMPLE3?spm_id_from=333.999.0.0&vd_source=0123456789abcdef0123456789abcdef',
		published_date: null,
		work_width: null,
		work_height: null,
		work_duration: null,
		title: null,
		description: null,
		source_id: 'SAMPLE3',
		uploader_id: null,
		is_pending: false,
		media: null
	},
	{
		id: '13',
		added_by: addedBy,
		thumbnail: null,
		media_title: 'Mirror',
		platform: Platform.SoundCloud,
		work_origin: WorkOrigin.Reupload,
		work_status: WorkStatus.Down,
		url: 'https://soundcloud.com/sample-user/sample4',
		published_date: '2023-05-14',
		work_width: null,
		work_height: null,
		work_duration: 250,
		title: 'A sample mirror that is no longer available',
		description: 'A sample description for the mirror.',
		source_id: 'sample4',
		uploader_id: null,
		is_pending: false,
		media: null
	},
	{
		id: '14',
		added_by: addedBy,
		thumbnail: null,
		media_title: 'Pending submission',
		platform: Platform.Twitter,
		work_origin: WorkOrigin.Author,
		work_status: WorkStatus.Available,
		url: 'https://twitter.com/sample_author/status/1234567890123456789',
		published_date: '2024-02-29',
		work_width: 720,
		work_height: 720,
		work_duration: 60,
		title: 'A sample clip that waits for approval',
		description: 'A sample description for the pending source.',
		source_id: '1234567890123456789',
		uploader_id: 'sample_author',
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
	}
];

const relatedWork = { id: '2', thumbnail: null, status: Status.Approved, title: 'A related work' };

const relations: [
	{ A_id: string; B_id: string; relation: WorkRelationTypes }[],
	(typeof relatedWork)[]
] = [[{ A_id: '1', B_id: '2', relation: WorkRelationTypes.Sequel }], [relatedWork]];

// `WikiEditor` picks the page whose `lang` matches the active locale, so the
// editor needs an English page to show content at the default locale. The
// language ids come from `$lib/enums/language`: English is 1 and Japanese is 2.
const wikiPage = [
	{ lang: 1, page: 'A sample wiki page in **markdown**.', title: null },
	{ lang: 2, page: 'サンプルの wiki ページです。**markdown** で書きます。', title: null }
];

// Fields that the `work/[work_id]` layout load returns (`WorkSchema`), plus
// `links`/`head` from the same layout. This page's own load adds `sources`.
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
	description: 'A sample description with an auto-linked URL: https://example.com'
};

const baseData = {
	stats,
	links,
	head,
	...baseWork,
	sources
};

const meta = {
	component: Page,
	args: {
		data: { ...baseData, user: memberUser },
		form: null
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

// A plain member sees the form and the source table. The origin select stays
// disabled for every approved source.
export const Member: Story = {};

// The work waits for approval, so a plain member can change the origin of each
// source.
export const MemberWithPendingWork: Story = {
	args: {
		data: { ...baseData, status: Status.Pending, user: memberUser }
	}
};

// An editor can change the origin of every source. The editor also gets a link
// that relists a source which is down.
export const Editor: Story = {
	args: {
		data: { ...baseData, user: editorUser }
	}
};

// A moderator gets the delete button below the source table.
export const Moderator: Story = {
	args: {
		data: { ...baseData, user: modUser }
	}
};

// The edit action failed, so the server sent the submitted values back.
export const WithFormError: Story = {
	args: {
		data: { ...baseData, user: memberUser },
		form: {
			failed: true,
			code: ErrorCode.Validation_Error,
			errorData: {},
			title: 'A sample title that the server refused',
			description: 'A sample description that the server refused.',
			rating: String(Rating.Sensitive),
			thumbnail_source_id: '11',
			reason: 'A sample reason for the edit.'
		}
	}
};
