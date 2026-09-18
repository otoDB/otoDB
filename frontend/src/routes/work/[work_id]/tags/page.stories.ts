import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { Levels, Rating, Status, WorkTagCategory } from '$lib/schema';
import Page from './+page.svelte';

const handlers = [
	http.get('*/api/wiki/page', () => HttpResponse.json([])),
	http.get('*/api/tag/search', () => HttpResponse.json({ items: [], count: 0 }))
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

const songTag = {
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
};

const creatorTag = {
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
};

const sourceTag = {
	id: '102',
	lang_prefs: [],
	aliased_to: null,
	name: 'Sample Source',
	slug: 'sample-source',
	category: WorkTagCategory.Media,
	deprecated: false,
	sample: true,
	creator_roles: null,
	primary_path: []
};

const generalTag = {
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
};

const suggestionSourceTag = {
	id: '200',
	lang_prefs: [],
	aliased_to: null,
	name: 'Suggested Source Tag',
	slug: 'suggested-source-tag',
	category: WorkTagCategory.Media,
	deprecated: false
};

const suggestionCreatorTag = {
	id: '201',
	lang_prefs: [],
	aliased_to: null,
	name: 'Suggested Creator Tag',
	slug: 'suggested-creator-tag',
	category: WorkTagCategory.Creator,
	deprecated: false
};

const suggestionNewTag = {
	id: '202',
	lang_prefs: [],
	aliased_to: null,
	name: 'Suggested New Tag',
	slug: 'suggested-new-tag',
	category: WorkTagCategory.General,
	deprecated: false
};

const baseWork = {
	id: '1',
	thumbnail_source_id: '10',
	thumbnail: null,
	pending_flag: null,
	pending_appeal: null,
	relations: [[], []] as [
		{ A_id: string; B_id: string; relation: number }[],
		{ id: string; thumbnail: string | null; status: Status; title: string }[]
	],
	rating: Rating.General,
	status: Status.Approved,
	wiki_page: [],
	title: 'A sample work title',
	description: 'A description with an auto-linked URL: https://example.com'
};

const baseData = {
	stats,
	links,
	head,
	user: memberUser,
	...baseWork,
	tags: [],
	suggestions: {
		title: null,
		description: null,
		source_tags: [],
		creator_tags: [],
		new_tags: []
	}
};

const meta = {
	component: Page,
	args: {
		data: baseData
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const MissingRequiredCategories: Story = {};

export const AllCategoriesPresent: Story = {
	args: {
		data: {
			...baseData,
			tags: [songTag, creatorTag, sourceTag, generalTag]
		}
	}
};

export const WithSuggestions: Story = {
	args: {
		data: {
			...baseData,
			suggestions: {
				title: null,
				description: null,
				source_tags: [suggestionSourceTag],
				creator_tags: [suggestionCreatorTag],
				new_tags: [suggestionNewTag]
			}
		}
	}
};

export const PendingWorkWithMixedSources: Story = {
	args: {
		data: {
			...baseData,
			status: Status.Pending,
			tags: [songTag, generalTag]
		}
	}
};
