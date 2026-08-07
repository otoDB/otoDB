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

const baseData = {
	stats,
	head,
	user: memberUser,
	batch_size
};

const commenter = (id: string, username: string, level: Levels) => ({
	id,
	username,
	level,
	date_created: '2023-01-15T09:00:00Z'
});

const workComment: Comment = {
	id: 'comment-1',
	user: commenter('1', 'member_user', Levels.Member),
	comment: 'The audio on this upload is much cleaner than the previous one.',
	submit_date: '2024-06-05T14:32:00Z',
	entity_type: 'mediawork',
	entity_id: '1'
};

const tagComment: Comment = {
	id: 'comment-2',
	user: commenter('2', 'editor_user', Levels.Editor),
	comment: 'Aliased this tag to the canonical spelling.',
	submit_date: '2024-06-05T13:50:00Z',
	entity_type: 'tagwork',
	entity_id: 'sample-tag'
};

const songComment: Comment = {
	id: 'comment-3',
	user: commenter('3', 'mod_user', Levels.Mod),
	comment: 'Merged the duplicate entry into this one.',
	submit_date: '2024-06-05T09:15:00Z',
	entity_type: 'mediasong',
	entity_id: '42'
};

const wikiComment: Comment = {
	id: 'comment-4',
	user: commenter('4', 'restricted_user', Levels.Restricted),
	comment:
		'A considerably longer comment that wraps onto several lines, so the table layout can be checked against realistic prose rather than a single short sentence. It also mentions https://example.com to show how raw URLs are rendered here.',
	submit_date: '2024-06-04T08:00:00Z',
	entity_type: 'wikipage',
	entity_id: 'style-guide'
};

const listComment: Comment = {
	id: 'comment-5',
	user: commenter('5', 'admin_user', Levels.Admin),
	comment: 'Great selection, thanks for putting this list together.',
	submit_date: '2024-05-27T18:20:00Z',
	entity_type: 'pool',
	entity_id: '7'
};

const profileComment: Comment = {
	id: 'comment-6',
	user: commenter('6', 'another_member', Levels.Member),
	comment: 'Welcome aboard!',
	submit_date: '2023-05-01T11:05:00Z',
	entity_type: 'account',
	entity_id: 'member_user'
};

const comments = [workComment, tagComment, songComment, wikiComment, listComment, profileComment];

const meta = {
	component: Page,
	args: {
		data: {
			...baseData,
			comments: { items: comments, count: comments.length }
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Default: Story = {};

export const Empty: Story = {
	args: {
		data: {
			...baseData,
			comments: { items: [], count: 0 }
		}
	}
};

/** `count` exceeds `batch_size`, so the pager is rendered below the table. */
export const Paginated: Story = {
	args: {
		data: {
			...baseData,
			comments: { items: comments, count: 137 }
		}
	}
};

export const SingleComment: Story = {
	args: {
		data: {
			...baseData,
			comments: { items: [workComment], count: 1 }
		}
	}
};
