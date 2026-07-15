import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels, ModelsWithComments } from '$lib/schema';
import CommentTree from './CommentTree.svelte';

const guestUser = null;

const memberUser = {
	csrf: 'token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const modUser = {
	csrf: 'token',
	user_id: '2',
	username: 'mod_user',
	level: Levels.Mod,
	prefs: {},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const baseProfile = {
	id: '1',
	level: Levels.Member,
	date_created: '2024-01-01T00:00:00Z',
	username: 'member_user'
};

const sampleComments = [
	{
		id: '100',
		user: baseProfile,
		comment: 'This is a top-level comment with some **bold** text.',
		submit_date: '2024-06-01T10:00:00Z',
		parent_id: '0',
		level: 0,
		index: 1,
		edited_at: null,
		edited_by: null
	},
	{
		id: '101',
		user: { ...baseProfile, id: '2', username: 'another_user' },
		comment: 'A reply to the first comment.',
		submit_date: '2024-06-01T11:00:00Z',
		parent_id: '100',
		level: 1,
		index: 2,
		edited_at: null,
		edited_by: null
	},
	{
		id: '102',
		user: baseProfile,
		comment: 'Another top-level comment.',
		submit_date: '2024-06-02T09:00:00Z',
		parent_id: '0',
		level: 0,
		index: 3,
		edited_at: '2024-06-02T10:00:00Z',
		edited_by: baseProfile
	}
];

const meta = {
	component: CommentTree,
	args: {
		model: ModelsWithComments.mediawork,
		pk: '1',
		user: guestUser,
		comments: []
	}
} satisfies Meta<ComponentProps<typeof CommentTree>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof CommentTree>>;

export const Empty: Story = {
	args: {
		user: guestUser,
		comments: []
	}
};

export const WithComments: Story = {
	args: {
		user: guestUser,
		comments: sampleComments
	}
};

export const AsMember: Story = {
	args: {
		user: memberUser,
		comments: sampleComments
	}
};

export const AsMod: Story = {
	args: {
		user: modUser,
		comments: sampleComments
	}
};

export const NoComments_AsMember: Story = {
	args: {
		user: memberUser,
		comments: []
	}
};
