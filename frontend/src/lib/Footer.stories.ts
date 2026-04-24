import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import Footer from './Footer.svelte';

const meta = {
	component: Footer,
	args: {
		user: null
	}
} satisfies Meta<ComponentProps<typeof Footer>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Footer>>;

export const Guest: Story = {
	args: {
		user: null
	}
};

export const LoggedIn: Story = {
	args: {
		user: { username: 'testuser' }
	}
};
