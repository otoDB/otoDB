import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels, SongTagCategory, type components } from '$lib/schema';
import Page from './+page.svelte';

type FatTagSong = components['schemas']['FatTagSongSchema'];
type TagSong = components['schemas']['TagSongSchema'];
type Song = components['schemas']['SongSchema'];
type Comment = components['schemas']['CommentSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const batch_size = 20;

// A popular attribute holds a few hundred songs, so the page is always a full
// batch with a pager under it. The count comes from the real page, but every
// value below is invented.
const total_count = 163;

const tag: FatTagSong = {
	id: '11',
	name: 'Example Genre',
	slug: 'example-genre',
	category: SongTagCategory.Genre,
	aliased_to: null,
	lang_prefs: [],
	children: []
};

const parentTag: TagSong = {
	id: '10',
	name: 'Example Parent Attribute',
	slug: 'example-parent-attribute',
	category: SongTagCategory.General,
	aliased_to: null,
	lang_prefs: []
};

const childTag: TagSong = {
	id: '12',
	name: 'Example Child Attribute',
	slug: 'example-child-attribute',
	category: SongTagCategory.Genre,
	aliased_to: null,
	lang_prefs: []
};

const aliasTag: TagSong = {
	id: '13',
	name: 'Example Genre Alias',
	slug: 'example-genre-alias',
	category: SongTagCategory.Genre,
	aliased_to: tag,
	lang_prefs: []
};

const links = [
	{ pathname: 'song_attribute/example-genre', title: 'Song Attribute example-genre' },
	{ pathname: 'song_attribute/example-genre/history', title: 'History' }
];

// An editor also gets the edit link in the section menu.
const editorLinks = [
	links[0],
	{ pathname: 'song_attribute/example-genre/edit', title: 'Edit' },
	links[1]
];

const editorUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'editor_user',
	level: Levels.Editor,
	prefs: {
		THEME: 0,
		VIDEO_PLATFORM: 0,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const comments: Comment[] = [
	{
		id: '1',
		user: {
			id: '2',
			username: 'member_user',
			level: Levels.Member,
			date_created: '2023-01-15T09:00:00Z'
		},
		comment: 'This attribute also covers the arrangements, not only the originals.',
		submit_date: '2024-06-01T10:00:00Z',
		parent_id: '0',
		level: 0,
		index: 0
	}
];

// The row templates cover the content shapes that decide the column widths: a
// short title, a long title with spaces, a long title with no break opportunity
// at all, a fixed BPM, and a variable BPM that renders the "N/A" placeholder.
const templates = [
	{
		work_tag: '101',
		title: 'Example Song One',
		bpm: 150,
		variable_bpm: false,
		author: 'Example Author'
	},
	{
		work_tag: '102',
		title: 'An Example Song With A Considerably Longer Title That Wraps Over Several Lines',
		bpm: 128,
		variable_bpm: false,
		author: 'Another Example Author'
	},
	{
		work_tag: '103',
		title: 'ExampleSongTitleWithoutAnySpacesAtAllWhichHasNoBreakOpportunityForTheTableLayout',
		bpm: null,
		variable_bpm: true,
		author: 'Example Author With A Long Name'
	},
	{
		work_tag: '104',
		title: 'Example Song Four',
		bpm: null,
		variable_bpm: true,
		author: 'Example Circle'
	},
	{
		work_tag: '105',
		title: 'Example Song Five',
		bpm: 213,
		variable_bpm: false,
		author: 'Example Composer'
	}
] satisfies Omit<Song, 'id' | 'tags'>[];

const songs: Song[] = Array.from({ length: batch_size }, (_, i) => ({
	...templates[i % templates.length],
	id: `song-${i + 1}`,
	tags: []
}));

const baseData = {
	user: null,
	stats,
	links,
	tag,
	tree: [parentTag, tag],
	aliases: [] as TagSong[],
	display_name: tag.name,
	head: {
		title: tag.name,
		breadcrumbs: [
			{ name: 'Home', url: '/' },
			{ name: 'Song Attribute', url: '/song_attribute' },
			{ name: tag.name, url: `/song_attribute/${tag.slug}` }
		]
	},
	songs: { items: songs, count: total_count },
	comments,
	batch_size
};

const meta = {
	component: Page,
	args: { data: baseData }
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** A logged out visitor sees a full batch of songs and the pager. */
export const Default: Story = {};

/** An editor also gets the edit link in the section menu and the comment form. */
export const Editor: Story = {
	args: {
		data: { ...baseData, user: editorUser, links: editorLinks }
	}
};

/** An attribute that carries child attributes and aliases. */
export const WithChildrenAndAliases: Story = {
	args: {
		data: {
			...baseData,
			tag: { ...tag, children: [childTag] },
			aliases: [aliasTag]
		}
	}
};
