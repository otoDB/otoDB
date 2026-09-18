import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import type { components } from '$lib/schema';
import Page from './+page.svelte';

type Song = components['schemas']['SongSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const batch_size = 20;

// Production serves roughly this many songs, 20 to a page, so the list is
// never short enough to render without a pager.
const total_count = 6998;

/** Every title and author here is invented. No real song data goes in a story. */
const templates: Omit<Song, 'id'>[] = [
	{
		work_tag: 'example-media-alpha',
		tags: [],
		title: 'Marmalade Skyline',
		author: 'Fictitious Ensemble',
		bpm: 128,
		variable_bpm: false
	},
	{
		work_tag: 'example-media-beta',
		tags: [],
		title: 'ぐるぐるパラダイス（架空バージョン）',
		author: '架空P',
		bpm: 174,
		variable_bpm: false
	},
	{
		// The tempo changes through the song, so the BPM cell shows the variable
		// label with the value in brackets.
		work_tag: 'example-media-gamma',
		tags: [],
		title: 'Tempo Drift Suite',
		author: 'Imaginary Orchestra',
		bpm: 96,
		variable_bpm: true
	},
	{
		// Nobody has filled in the tempo yet, so the BPM cell falls back.
		work_tag: 'example-media-delta',
		tags: [],
		title: 'Untitled Practice Loop',
		author: 'Nonexistent Duo',
		bpm: null,
		variable_bpm: false
	},
	{
		work_tag: 'example-media-epsilon',
		tags: [],
		title: 'Glass Harbour (Extended Mix)',
		author: 'Made-Up Collective',
		bpm: 140.5,
		variable_bpm: false
	},
	{
		// A single run of characters with no break opportunity. The table uses auto
		// layout, so this title stretches the first column and squeezes the rest.
		work_tag: 'example-media-zeta',
		tags: [],
		title:
			'SUPERLONGUNBREAKABLETITLEWITHOUTANYWHITESPACEATALLTHATSTRETCHESTHEFIRSTCOLUMNVERYFARINDEED',
		author: 'Invented Soloist',
		bpm: 200,
		variable_bpm: true
	},
	{
		work_tag: 'example-media-eta',
		tags: [],
		title: 'Paper Lantern Parade',
		author: 'Pretend Quartet',
		bpm: 87,
		variable_bpm: false
	},
	{
		work_tag: 'example-media-theta',
		tags: [],
		title: 'Copper Wire Lullaby',
		author: 'Hypothetical Band',
		bpm: 112,
		variable_bpm: false
	}
];

/** A full page of songs, as the real list always is. */
const songs: Song[] = Array.from({ length: batch_size }, (_, i) => ({
	...templates[i % templates.length],
	id: String(i + 1)
}));

const baseData = {
	user: null,
	stats,
	query: '',
	query_tags: '',
	results: { items: songs, count: total_count },
	batch_size,
	bpm_range: null as [number, number] | null,
	author: '',
	head: {
		title: m.mild_loud_shad_enchant({
			type: m.mean_top_antelope_love(),
			name: m.grand_nice_pony_belong()
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

/** The unfiltered list: a full batch of songs with the pager below it. */
export const Default: Story = {};

/** A search narrows the list to one page, so the pager disappears. */
export const Filtered: Story = {
	args: {
		data: {
			...baseData,
			query: 'lantern',
			query_tags: 'example-song-tag',
			author: 'Pretend Quartet',
			bpm_range: [80, 120],
			results: { items: [{ ...templates[6], id: '7' }], count: 1 }
		}
	}
};

/**
 * The list itself is never empty, but a narrow enough search matches nothing,
 * and that is the only way to see this state.
 */
export const FilteredNoResults: Story = {
	args: {
		data: {
			...baseData,
			query: 'no-such-song',
			bpm_range: [400, 500],
			results: { items: [], count: 0 }
		}
	}
};
