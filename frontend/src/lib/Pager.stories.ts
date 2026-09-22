import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import Pager from './Pager.svelte';

const meta = {
	component: Pager,
	args: {
		n_count: 100,
		page_size: 10
	}
} satisfies Meta<ComponentProps<typeof Pager>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Pager>>;

export const FirstPage: Story = {
	parameters: {
		sveltekit_experimental: {
			state: { page: { url: new URL('https://example.com/items?page=1') } }
		}
	}
};

export const MiddlePage: Story = {
	parameters: {
		sveltekit_experimental: {
			state: { page: { url: new URL('https://example.com/items?page=5') } }
		}
	}
};

export const LastPage: Story = {
	parameters: {
		sveltekit_experimental: {
			state: { page: { url: new URL('https://example.com/items?page=10') } }
		}
	}
};
