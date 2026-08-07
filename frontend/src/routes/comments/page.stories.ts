import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels, type components } from '$lib/schema';
import Page from './+page.svelte';

type Comment = components['schemas']['ExtCommentSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = { title: m.same_broad_haddock_pinch() };

const memberUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {
		THEME: 0,
		VIDEO_PLATFORM: 0,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const batch_size = 20;

// The real endpoint has several thousand comments behind it, so the page is
// effectively always a full batch with a pager.
const total_count = 4317;

const commenter = (id: string, username: string, level: Levels) => ({
	id,
	username,
	level,
	date_created: '2023-01-15T09:00:00Z'
});

// One template per entity type `buildEntityRoutes` knows about, so every link
// shape the table can produce is exercised. A couple of them deliberately carry
// unbreakable content — a bare long URL, a long tag slug — because those are what
// used to blow the column widths out and push the table past the section.
const templates = [
	{
		user: commenter('1', 'member_user', Levels.Member),
		comment: 'The audio on this upload is much cleaner than the previous one.',
		entity_type: 'mediawork',
		entity_id: '1'
	},
	{
		user: commenter('2', 'editor_user', Levels.Editor),
		comment: 'Aliased this tag to the canonical spelling.',
		entity_type: 'tagwork',
		entity_id: 'a-deliberately-long-sample-tag-slug'
	},
	{
		user: commenter('3', 'mod_user', Levels.Mod),
		comment: 'Merged the duplicate entry into this one.',
		entity_type: 'mediasong',
		entity_id: '42'
	},
	{
		user: commenter('4', 'restricted_user', Levels.Restricted),
		comment:
			'A considerably longer comment that wraps onto several lines, so the table layout can be checked against realistic prose rather than a single short sentence. It also pastes a bare source link, https://example.com/watch?v=aVeryLongVideoIdentifier&list=AnEquallyLongPlaylistIdentifier&index=12, which has no break opportunity in it at all.',
		entity_type: 'wikipage',
		entity_id: 'style-guide'
	},
	{
		user: commenter('5', 'admin_user', Levels.Admin),
		comment: 'Great selection, thanks for putting this list together.',
		entity_type: 'pool',
		entity_id: '7'
	},
	{
		user: commenter('6', 'another_member', Levels.Member),
		comment: 'Welcome aboard!',
		entity_type: 'account',
		entity_id: 'member_user'
	}
] satisfies Omit<Comment, 'id' | 'submit_date'>[];

// Fixed anchor, not the current clock, so the story renders the same thing on
// every open and can serve as a regression-test baseline.
const NEWEST_SUBMIT_DATE = Date.parse('2024-06-05T14:32:00Z');

const comments: Comment[] = Array.from({ length: batch_size }, (_, i) => ({
	...templates[i % templates.length],
	id: `comment-${i + 1}`,
	submit_date: new Date(NEWEST_SUBMIT_DATE - i * 7 * 60 * 1000).toISOString()
}));

const meta = {
	component: Page,
	args: {
		data: {
			stats,
			head,
			user: memberUser,
			batch_size,
			comments: { items: comments, count: total_count }
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** A full batch of `batch_size` comments with the pager below the table. */
export const Default: Story = {};
