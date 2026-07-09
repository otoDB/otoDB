import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import {
	Levels,
	SongConnectionTypes,
	SongRelationTypes,
	Status,
	TagWorkConnectionTypes,
	WorkTagCategory,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type TagWorkConnection = components['schemas']['TagWorkConnectionSchema'];
type TagWorkExtraConnection = components['schemas']['TagWorkExtraConnectionSchema'];
type Connections = [TagWorkConnection[], TagWorkExtraConnection[] | null];
type ThinWork = components['schemas']['ThinWorkSchema'];
type TagWorkSchema = components['schemas']['TagWorkSchema'];
type Comment = components['schemas']['CommentSchema'];

const handlers = [
	http.get('*/api/wiki/page', () => HttpResponse.json([])),
	http.get('*/api/tag/search', () => HttpResponse.json({ items: [], count: 0 }))
];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const links = [
	{ pathname: 'tag/example-tag', title: 'Example Tag' },
	{ pathname: 'tag/example-tag/threads', title: 'Threads' },
	{ pathname: 'tag/example-tag/history', title: 'History' }
];

const mediaTag = {
	id: '1',
	children: [] as TagWorkSchema[],
	song: null,
	media_type: [1],
	lang_prefs: [],
	aliased_to: null,
	category: WorkTagCategory.Media,
	name: 'Example Media Tag',
	slug: 'example-media-tag',
	deprecated: false
};

const parentTag = {
	id: '2',
	lang_prefs: [],
	aliased_to: null,
	name: 'Parent Tag',
	slug: 'parent-tag',
	category: WorkTagCategory.Source,
	deprecated: false
};

const aliasTag = {
	id: '3',
	lang_prefs: [],
	aliased_to: null,
	name: 'Alias Tag',
	slug: 'alias-tag',
	category: WorkTagCategory.Media,
	deprecated: false
};

const childTag: TagWorkSchema = {
	id: '4',
	lang_prefs: [],
	aliased_to: null,
	name: 'Child Tag',
	slug: 'child-tag',
	category: WorkTagCategory.Media,
	deprecated: false
};

const commentAuthor = {
	id: '1',
	username: 'member_user',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z'
};

const sampleComments: Comment[] = [
	{
		id: '1',
		user: commentAuthor,
		comment: 'This tag needs more works attached.',
		submit_date: '2024-06-01T10:00:00Z',
		parent_id: '0',
		level: 0,
		index: 0
	}
];

const sampleWorks: ThinWork[] = [
	{
		id: '1',
		tags: [],
		thumbnail: null,
		status: Status.Approved,
		title: 'Example Work 1'
	},
	{
		id: '2',
		tags: [],
		thumbnail: null,
		status: Status.Approved,
		title: 'Example Work 2'
	}
];

const baseData = {
	user: null,
	stats,
	links,
	song_links: null,
	tag: mediaTag,
	song_relations: null,
	display_name: mediaTag.name,
	head: {
		title: mediaTag.name,
		breadcrumbs: [
			{ name: 'Home', url: '/' },
			{ name: 'Tags', url: '/tag' },
			{ name: mediaTag.name, url: `/tag/${mediaTag.slug}` }
		]
	},
	wiki_page: [],
	paths: [[], {}] as [(typeof parentTag)[], Record<string, string[]>],
	aliases: [] as (typeof aliasTag)[],
	primary_parent: null as string | null,
	connections: [[], []] as Connections,
	song_connections: null,
	works: { items: sampleWorks, count: sampleWorks.length },
	comments: sampleComments,
	batch_size: 20,
	similar: Promise.resolve([])
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

export const MediaTag: Story = {};

export const WithChildTags: Story = {
	args: {
		data: {
			...baseData,
			tag: {
				...mediaTag,
				children: [childTag]
			}
		}
	}
};

export const SongTag: Story = {
	args: {
		data: {
			...baseData,
			tag: {
				...mediaTag,
				id: '10',
				category: WorkTagCategory.Song,
				name: 'Example Song Tag',
				slug: 'example-song-tag',
				media_type: null,
				song: {
					id: '100',
					work_tag: '10',
					tags: [],
					title: 'Example Song',
					bpm: 128,
					variable_bpm: false,
					author: 'Example Author'
				}
			},
			song_links: [
				{ pathname: 'tag/example-song-tag', title: 'Song 100' },
				{ pathname: 'tag/example-song-tag/song_tags', title: 'Song Tags' },
				{ pathname: 'tag/example-song-tag/history', title: 'History' }
			],
			display_name: 'Example Song Tag',
			head: {
				title: 'Example Song Tag',
				breadcrumbs: [
					{ name: 'Home', url: '/' },
					{ name: 'Tags', url: '/tag' },
					{ name: 'Example Song Tag', url: '/tag/example-song-tag' }
				]
			},
			song_relations: [
				[{ A_id: '100', B_id: '200', relation: SongRelationTypes.Remix }],
				[
					{
						id: '200',
						work_tag: '20',
						title: 'Original Song',
						bpm: 120,
						variable_bpm: false,
						author: 'Original Author'
					}
				]
			],
			song_connections: [
				{ site: SongConnectionTypes.VGMdb, content_id: '1234', dead: false },
				{ site: SongConnectionTypes.VocaDB, content_id: 'S5678', dead: false }
			]
		}
	}
};

export const WithParentsAndAliases: Story = {
	args: {
		data: {
			...baseData,
			paths: [[parentTag], { 'example-media-tag': [parentTag.slug] }] as [
				(typeof parentTag)[],
				Record<string, string[]>
			],
			aliases: [aliasTag],
			primary_parent: parentTag.slug,
			connections: [
				[
					{
						site: TagWorkConnectionTypes.Niconico_Encyclopedia,
						content_id: 'example-media-tag',
						dead: false
					}
				],
				[]
			] as Connections
		}
	}
};

export const EmptyWorks: Story = {
	args: {
		data: {
			...baseData,
			works: { items: [], count: 0 },
			comments: []
		}
	}
};
