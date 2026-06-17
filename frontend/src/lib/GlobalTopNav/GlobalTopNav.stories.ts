import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import GlobalTopNav from './GlobalTopNav.svelte';

const meta = {
	component: GlobalTopNav,
	args: {
		user: null
	}
} satisfies Meta<ComponentProps<typeof GlobalTopNav>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof GlobalTopNav>>;

export const Guest: Story = {
	args: {
		user: null
	}
};

export const LoggedIn: Story = {
	args: {
		user: {
			username: 'testuser'
		}
	}
};
