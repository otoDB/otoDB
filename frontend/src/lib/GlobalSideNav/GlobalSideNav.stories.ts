import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { Levels } from '$lib/schema';
import GlobalSideNav from './GlobalSideNav.svelte';

const defaultStats = {
	works: 1234,
	tags: 567,
	songs: 89,
	lists: 42
};

const meta = {
	component: GlobalSideNav,
	args: {
		isMobileNavOpen: true,
		closeMobileNav: () => {},
		user: null,
		stats: defaultStats
	}
} satisfies Meta<ComponentProps<typeof GlobalSideNav>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof GlobalSideNav>>;

export const Guest: Story = {
	args: {
		user: null
	}
};

export const Member: Story = {
	args: {
		user: {
			level: Levels.Member,
			username: 'testuser',
			notifs_count: 0,
			notifs_nonsub_count: 0
		}
	}
};

export const MemberWithNotifications: Story = {
	args: {
		user: {
			level: Levels.Member,
			username: 'testuser',
			notifs_count: 5,
			notifs_nonsub_count: 3
		}
	}
};

export const Editor: Story = {
	args: {
		user: {
			level: Levels.Editor,
			username: 'editoruser',
			notifs_count: 0,
			notifs_nonsub_count: 0
		}
	}
};

export const Admin: Story = {
	args: {
		user: {
			level: Levels.Admin,
			username: 'adminuser',
			notifs_count: 0,
			notifs_nonsub_count: 0
		}
	}
};

export const MobileNavClosed: Story = {
	args: {
		isMobileNavOpen: false,
		user: null
	}
};
