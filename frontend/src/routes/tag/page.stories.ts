import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { WorkTagCategory, type components } from '$lib/schema';
import Page from './+page.svelte';

type TagWorkSearchResult = components['schemas']['TagWorkSearchResultSchema'];

const results: TagWorkSearchResult[] = [
	{
		id: '1',
		lang_prefs: [],
		aliased_to: null,
		name: 'Example Media Tag',
		slug: 'example-media-tag',
		category: WorkTagCategory.Media,
		deprecated: false,
		n_instance: 42
	},
	{
		id: '2',
		lang_prefs: [],
		aliased_to: null,
		name: 'Example Song Tag',
		slug: 'example-song-tag',
		category: WorkTagCategory.Song,
		deprecated: false,
		n_instance: 17
	},
	{
		id: '3',
		lang_prefs: [],
		aliased_to: null,
		name: 'Example Source Tag',
		slug: 'example-source-tag',
		category: WorkTagCategory.Source,
		deprecated: true,
		n_instance: 3
	}
];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const baseData = {
	user: null,
	stats,
	query: '',
	category: -1,
	results: { items: results, count: results.length },
	batch_size: 20,
	media_type: [],
	order: 'newest',
	deprecated_only: false,
	hide_orphans: true,
	wiki_lang: [],
	wiki_lang_missing: [],
	lang_pref: [],
	lang_pref_missing: [],
	has_connections: null,
	min_parents: undefined,
	max_parents: undefined,
	head: {
		title: m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.empty_legal_chicken_taste()
		})
	}
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Default: Story = {};

export const WithQuery: Story = {
	args: {
		data: {
			...baseData,
			query: 'example'
		}
	}
};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			results: { items: [], count: 0 }
		}
	}
};

export const ManyPages: Story = {
	args: {
		data: {
			...baseData,
			results: { items: results, count: 250 }
		}
	}
};
