import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import {
	EntityModels,
	Levels,
	Route,
	Status,
	WorkRelationTypes,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type RC = components['schemas']['RevisionChangeSchema'];
type OldColumn = components['schemas']['OldColumnSchema'];
type SlimWork = components['schemas']['SlimWorkSchema'];

const handlers = [
	http.post('*/api/history/rollback', () => new HttpResponse(null, { status: 200 }))
];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const loggedInMod = {
	csrf: 'csrf-token',
	user_id: '9',
	username: 'mod_user',
	level: Levels.Mod,
	prefs: {
		THEME: 0,
		VIDEO_PLATFORM: 0,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const rc = (
	overrides: Partial<RC> &
		Pick<RC, 'target_type' | 'target_id' | 'ent_type' | 'ent_id' | 'route' | 'tg_id'>
): RC => ({
	created: false,
	deleted: false,
	restored: false,
	...overrides
});

// Route 1: a plain field edit on the entity itself (mediawork title)
const titleRow = {
	target_type: 'mediawork',
	tg_id: '1',
	target_id: '1',
	rcs: [
		rc({
			target_type: 'mediawork',
			target_id: '1',
			ent_type: 'mediawork',
			ent_id: '1',
			route: Route.Media_Work_Update,
			tg_id: '1',
			target_column: 'title',
			old_value: 'Old Title',
			target_value: 'New Title'
		})
	]
};

// Route 2: a newly-created relation between two works, rendered as work cards
const works: SlimWork[] = [
	{ id: '100', thumbnail: null, status: Status.Approved, title: 'Example Anime OP' },
	{ id: '200', thumbnail: null, status: Status.Approved, title: 'Example Anime ED' }
];

const relationRow = {
	target_type: 'workrelation',
	tg_id: '1',
	target_id: '50',
	rcs: [
		rc({
			target_type: 'workrelation',
			target_id: '50',
			ent_type: 'mediawork',
			ent_id: '1',
			route: Route.Work_Relation_Control,
			tg_id: '1',
			target_column: 'A',
			ref: EntityModels.mediawork,
			target_value: '100',
			created: true
		}),
		rc({
			target_type: 'workrelation',
			target_id: '50',
			ent_type: 'mediawork',
			ent_id: '1',
			route: Route.Work_Relation_Control,
			tg_id: '1',
			target_column: 'B',
			ref: EntityModels.mediawork,
			target_value: '200',
			created: true
		}),
		rc({
			target_type: 'workrelation',
			target_id: '50',
			ent_type: 'mediawork',
			ent_id: '1',
			route: Route.Work_Relation_Control,
			tg_id: '1',
			target_column: 'relation',
			target_value: String(WorkRelationTypes.Respect),
			created: true
		})
	]
};

// Route 3: a fully-removed connection row (no A/B), shown via deleted_rows
const deletedRow = {
	target_type: 'tagworkconnection',
	tg_id: '10',
	target_id: '30',
	rcs: [
		rc({
			target_type: 'tagworkconnection',
			target_id: '30',
			ent_type: 'tagwork',
			ent_id: '10',
			route: Route.Tag_Work_Delete,
			tg_id: '10',
			deleted: true
		})
	]
};
const deletedRows: Record<string, OldColumn[]> = {
	'tagworkconnection:30': [
		{ column: 'site', value: '20' },
		{ column: 'content_id', value: 'old-wiki-slug' }
	]
};

// Route 4: a long text diff with an unchanged, windowed-out middle section
const wikiRow = {
	target_type: 'wikipage',
	tg_id: '5',
	target_id: '5',
	rcs: [
		rc({
			target_type: 'wikipage',
			target_id: '5',
			ent_type: 'wikipage',
			ent_id: '5',
			route: Route.Wiki_Edit,
			tg_id: '5',
			target_column: 'page',
			diff: [
				{ op: 0, text: 'This is the unchanged intro paragraph of the wiki page. ' },
				{
					op: 2,
					text: 'A long stretch of unchanged body text that gets collapsed behind the windowed-diff toggle. '
				},
				{ op: -1, text: 'This sentence was removed. ' },
				{ op: 1, text: 'This sentence was added instead. ' },
				{ op: 2, text: 'Another long unchanged trailing section, also windowed out by default. ' }
			]
		})
	]
};

const baseData = {
	stats,
	user: null,
	revision: {
		id: '42',
		date: '2024-06-01T12:00:00Z',
		user: 'member_user',
		index: 1,
		route: Route.Media_Work_Update,
		message: ''
	},
	changes: {
		changes: [...titleRow.rcs],
		works: [],
		labels: {},
		deleted_rows: {},
		row_context: {}
	},
	routes: [
		{
			route: Route.Media_Work_Update,
			entities: [{ ent_type: 'mediawork' as const, ent_id: '1', rows: [titleRow] }]
		}
	]
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

export const SimpleFieldEdit: Story = {};

export const ModeratorWithRevertAndRelations: Story = {
	args: {
		data: {
			...baseData,
			user: loggedInMod,
			revision: {
				...baseData.revision,
				id: '43',
				route: Route.Work_Relation_Control,
				message: 'Linking the OP and ED as related works, and removing a stale wiki link.'
			},
			changes: {
				changes: [...relationRow.rcs, ...deletedRow.rcs],
				works,
				labels: {},
				deleted_rows: deletedRows,
				row_context: {}
			},
			routes: [
				{
					route: Route.Work_Relation_Control,
					entities: [{ ent_type: 'mediawork', ent_id: '1', rows: [relationRow] }]
				},
				{
					route: Route.Tag_Work_Delete,
					entities: [{ ent_type: 'tagwork', ent_id: '10', rows: [deletedRow] }]
				}
			]
		}
	}
};

export const WindowedTextDiff: Story = {
	args: {
		data: {
			...baseData,
			revision: {
				...baseData.revision,
				id: '44',
				route: Route.Wiki_Edit,
				message: ''
			},
			changes: {
				changes: [...wikiRow.rcs],
				works: [],
				labels: {},
				deleted_rows: {},
				row_context: {}
			},
			routes: [
				{
					route: Route.Wiki_Edit,
					entities: [{ ent_type: 'wikipage', ent_id: '5', rows: [wikiRow] }]
				}
			]
		}
	}
};
