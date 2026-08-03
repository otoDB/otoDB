import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import {
	Levels,
	Platform,
	WorkOrigin,
	WorkStatus,
	WorkTagCategory,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type TagWorkSchema = components['schemas']['TagWorkSchema'];
type Suggestions = components['schemas']['SourceSuggestionsResponse'];

const handlers = [
	http.get('*/api/tag/search', () => HttpResponse.json({ items: [], count: 0 })),
	http.get('*/api/tag/tag', () => HttpResponse.json(null, { status: 404 })),
	http.get('*/api/work/search', () => HttpResponse.json({ items: [], count: 0 }))
];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const sourceId = '42';

const links = [
	{ pathname: `upload/${sourceId}`, title: `Source ${sourceId}` },
	{ pathname: `upload/${sourceId}/moderation`, title: 'Moderation' }
];

const head = { title: `Source ${sourceId}` };

const memberUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const addedBy = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

const source = {
	id: sourceId,
	added_by: addedBy,
	thumbnail: null,
	media_title: null,
	platform: Platform.YouTube,
	work_origin: WorkOrigin.Author,
	work_status: WorkStatus.Available,
	url: 'https://www.youtube.com/watch?v=sample1',
	published_date: '2024-01-05',
	work_width: 1920,
	work_height: 1080,
	work_duration: 245,
	title: 'A sample uploaded video',
	description: 'A description with an auto-linked URL: https://example.com',
	source_id: null,
	uploader_id: null,
	is_pending: false,
	media: null
};

const tag = (id: string, name: string, slug: string, category: WorkTagCategory): TagWorkSchema => ({
	id,
	lang_prefs: [],
	aliased_to: null,
	name,
	slug,
	category,
	deprecated: false
});

const suggestions: Suggestions = {
	title: 'A sample uploaded video',
	description: 'A description with an auto-linked URL: https://example.com',
	source_tags: [tag('100', 'Sample Media Source', 'sample-media-source', WorkTagCategory.Media)],
	creator_tags: [tag('101', 'Sample Creator', 'sample-creator', WorkTagCategory.Creator)],
	new_tags: [tag('102', 'Sample Song', 'sample-song', WorkTagCategory.Song)]
};

const baseData = {
	user: memberUser,
	stats,
	source,
	sourceId,
	links,
	head,
	suggestions,
	isBound: false
};

const meta = {
	component: Page,
	args: { data: baseData },
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** Unbound source with tag suggestions: the create/bind switch and the work creation form. */
export const WithSuggestions: Story = {};

/** Unbound source whose metadata could not be fetched and for which no tags were suggested. */
export const NoSuggestions: Story = {
	args: {
		data: {
			...baseData,
			source: {
				...source,
				title: null,
				description: null,
				published_date: null,
				work_width: null,
				work_height: null,
				work_duration: null
			},
			suggestions: null
		}
	}
};

/** A source still awaiting metadata retrieval, showing the pending banner. */
export const PendingSource: Story = {
	args: {
		data: {
			...baseData,
			source: { ...source, is_pending: true }
		}
	}
};

/** A source already bound to a work: the forms are replaced by a link to that work. */
export const BoundToWork: Story = {
	args: {
		data: {
			...baseData,
			source: { ...source, media: 7, media_title: 'An existing work' },
			suggestions: null,
			isBound: true
		}
	}
};

/** A source uploaded by someone other than the author, viewed by a logged out visitor. */
export const ReuploadAsGuest: Story = {
	args: {
		data: {
			...baseData,
			user: null,
			source: {
				...source,
				work_origin: WorkOrigin.Reupload,
				work_status: WorkStatus.Down,
				media: 7,
				media_title: 'An existing work'
			},
			suggestions: null,
			isBound: true
		}
	}
};
