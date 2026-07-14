import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Status, WorkTagCategory } from '$lib/schema';
import Page from './+page.svelte';

const mediaTag = {
	id: '1',
	lang_prefs: [],
	aliased_to: null,
	name: 'Example Media Tag',
	slug: 'example-media-tag',
	category: WorkTagCategory.Media,
	deprecated: false,
	sample: false,
	creator_roles: null
};

const songTag = {
	id: '2',
	lang_prefs: [],
	aliased_to: null,
	name: 'Example Song Tag',
	slug: 'example-song-tag',
	category: WorkTagCategory.Song,
	deprecated: false,
	sample: false,
	creator_roles: null
};

const sampleWorks = [
	{
		id: '1',
		tags: [mediaTag, songTag],
		thumbnail: null,
		status: Status.Approved,
		title: 'Example Work One'
	},
	{
		id: '2',
		tags: [mediaTag],
		thumbnail: null,
		status: Status.Approved,
		title: 'Example Work Two'
	},
	{
		id: '3',
		tags: [],
		thumbnail: null,
		status: Status.Pending,
		title: 'Example Work Three'
	}
];

const links = [
	{ pathname: 'work', title: 'Works' },
	{ pathname: 'tag', title: 'Tags' },
	{ pathname: 'song', title: 'Songs' },
	{ pathname: 'song_attribute', title: 'Song Attributes' },
	{ pathname: 'list', title: 'Lists' }
];

const baseData = {
	user: null,
	stats: { works: 1234, tags: 567, songs: 89, lists: 42 },
	links,
	query: '',
	query_tags: '',
	results: { items: sampleWorks, count: sampleWorks.length },
	batch_size: 20,
	head: {
		title: m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.grand_merry_fly_succeed()
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

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			results: { items: [], count: 0 }
		}
	}
};

export const SearchResults: Story = {
	args: {
		data: {
			...baseData,
			query: 'touhou',
			query_tags: 'touhou',
			results: { items: [sampleWorks[0]], count: 1 }
		}
	}
};

export const ManyPages: Story = {
	args: {
		data: {
			...baseData,
			results: { items: sampleWorks, count: 120 }
		}
	}
};
