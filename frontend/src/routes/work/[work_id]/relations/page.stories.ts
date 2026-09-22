import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels, Status, WorkRelationTypes, type components } from '$lib/schema';
import { enumValues } from '$lib/enums';
import { m } from '$lib/paraglide/messages.js';
import Page from './+page.svelte';

type WorkRelation = components['schemas']['WorkRelationSchema'];
type SlimWork = components['schemas']['SlimWorkSchema'];

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
	description: m.plain_witty_crane_hum(),
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

const baseWork = {
	id: '1',
	thumbnail_source_id: null,
	tags: [],
	thumbnail: null,
	pending_flag: null,
	pending_appeal: null,
	rating: 0,
	status: Status.Approved,
	wiki_page: [],
	title: 'A sample work title',
	description: null
};

const baseData = {
	stats,
	links,
	head,
	user: memberUser,
	...baseWork,
	relations: [[], []] as [WorkRelation[], SlimWork[]]
};

const meta = {
	component: Page,
	args: {
		data: baseData
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

// `+page.server.ts` returns nothing when the work has no relations, so
// `data.works` stays undefined and the page falls back to a text message.
export const NoRelations: Story = {};

// The backend puts both ends of every relation into `works`, so the centre
// work is always present.
const relatedWorks: SlimWork[] = [
	{ id: '1', thumbnail: null, status: Status.Approved, title: 'A sample work title' },
	{
		id: '2',
		thumbnail: '/storybook-static/thumbnail_1280x720.jpg',
		status: Status.Approved,
		title: 'A sequel work'
	},
	{ id: '3', thumbnail: null, status: Status.Approved, title: 'A work that respects it' },
	{ id: '4', thumbnail: null, status: Status.Approved, title: null },
	{ id: '5', thumbnail: null, status: Status.Approved, title: 'A sampled work' },
	{ id: '6', thumbnail: null, status: Status.Approved, title: 'A work two hops away' }
];

// The backend returns the whole connected component. Work #3 gives a relation
// that holds the centre work in `B_id`. Work #6 sits two hops from the centre,
// so the depth control has an effect.
const relations: WorkRelation[] = [
	{ A_id: '1', B_id: '2', relation: WorkRelationTypes.Sequel },
	{ A_id: '3', B_id: '1', relation: WorkRelationTypes.Respect },
	{ A_id: '1', B_id: '4', relation: WorkRelationTypes.Collab_Part },
	{ A_id: '1', B_id: '5', relation: WorkRelationTypes.Sample },
	{ A_id: '2', B_id: '6', relation: WorkRelationTypes.Sample }
];

export const WithRelations: Story = {
	tags: ['!dev', '!test'], // TODO: disabled for now
	args: {
		data: {
			...baseData,
			relations: [relations, relatedWorks],
			works: relatedWorks,
			svg: '',
			direction: 'TB' as const,
			allowed_types: enumValues(WorkRelationTypes),
			degree: 1,
			max_distance: 2,
			show_thumbs: true
		}
	}
};
