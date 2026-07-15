import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { expect, userEvent, within } from 'storybook/test';
import {
	LanguageTypes,
	SongConnectionTypes,
	SongRelationTypes,
	TagWorkConnectionTypes,
	WorkTagCategory,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type TagWorkConnection = components['schemas']['TagWorkConnectionSchema'];
type TagWorkExtraConnection = components['schemas']['TagWorkExtraConnectionSchema'];
type Connections = [TagWorkConnection[], TagWorkExtraConnection[] | null];

const handlers = [
	http.get('*/api/wiki/page', () => HttpResponse.json([])),
	http.get('*/api/tag/search', () => HttpResponse.json({ items: [], count: 0 }))
];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const links = [
	{ pathname: 'tag/example-tag', title: 'Example Tag' },
	{ pathname: 'tag/example-tag/edit', title: 'Edit' },
	{ pathname: 'tag/example-tag/threads', title: 'Threads' },
	{ pathname: 'tag/example-tag/history', title: 'History' }
];

const mediaTag = {
	id: '1',
	children: [],
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
	parents: [],
	details: {
		paths: [[], {}] as [(typeof parentTag)[], Record<string, string[]>],
		wiki_page: [],
		aliases: [],
		primary_parent: null
	},
	connections: [[], []] as Connections,
	song_connections: null
};

const meta = {
	component: Page,
	args: {
		data: baseData,
		form: undefined
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const MediaTag: Story = {};

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
				{ pathname: 'tag/example-song-tag/edit', title: 'Edit' },
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

export const SubmittingConnectionsSendsRequest: Story = {
	play: async ({ canvasElement }) => {
		const form = canvasElement.querySelector('form[action="?/connections"]');
		if (!(form instanceof HTMLElement)) throw new Error('connections form not found');
		const formCanvas = within(form);

		await userEvent.type(
			formCanvas.getByRole('textbox'),
			'https://bsky.app/profile/example.bsky.social'
		);
		await userEvent.click(formCanvas.getByRole('button', { name: 'Add' }));

		const submitInput = form.querySelector('input[type="submit"]');
		if (!(submitInput instanceof HTMLElement)) throw new Error('submit input not found');

		// @storybook/sveltekit mocks `enhance` from `$app/forms`: instead of performing a
		// real fetch, it prevents the default submission and dispatches this window event
		// with the original SubmitEvent, which is what confirms the form would have submitted.
		const submitEventPromise = new Promise<SubmitEvent>((resolve) => {
			window.addEventListener(
				'storybook:enhance',
				(e) => resolve((e as CustomEvent<[SubmitEvent]>).detail[0]),
				{ once: true }
			);
		});

		await userEvent.click(submitInput);
		const submitEvent = await submitEventPromise;

		const submittedForm = submitEvent.target;
		if (!(submittedForm instanceof HTMLFormElement)) throw new Error('unexpected submit target');

		await expect(new FormData(submittedForm).get('urls')).toContain(
			'bsky.app/profile/example.bsky.social'
		);
	}
};

export const WithParentsAndAliases: Story = {
	args: {
		data: {
			...baseData,
			tag: {
				...mediaTag,
				lang_prefs: [{ tag: '1', slug: 'example-media-tag', lang: LanguageTypes.en }]
			},
			parents: [parentTag],
			details: {
				paths: [[parentTag], { 'example-media-tag': [parentTag.slug] }] as [
					(typeof parentTag)[],
					Record<string, string[]>
				],
				wiki_page: [],
				aliases: [aliasTag],
				primary_parent: parentTag.slug
			},
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
