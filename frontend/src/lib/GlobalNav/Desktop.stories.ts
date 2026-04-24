import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels } from '$lib/schema';
import GlobalNav from './Desktop.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const meta = {
	component: GlobalNav,
	args: {
		user: null,
		stats
	}
} satisfies Meta<ComponentProps<typeof GlobalNav>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof GlobalNav>>;

export const Guest: Story = {
	args: { user: null, stats }
};

export const Member: Story = {
	args: {
		user: {
			username: 'member',
			level: Levels.Member,
			notifs_count: 0
		},
		stats
	}
};

export const Editor: Story = {
	args: {
		user: {
			username: 'editor',
			level: Levels.Editor,
			notifs_count: 0
		},
		stats
	}
};

export const Admin: Story = {
	args: {
		user: {
			username: 'admin',
			level: Levels.Admin,
			notifs_count: 0
		},
		stats
	}
};
