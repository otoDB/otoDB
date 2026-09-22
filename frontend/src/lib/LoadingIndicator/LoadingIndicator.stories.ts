import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import LoadingIndicator from './LoadingIndicator.svelte';

const meta = {
	component: LoadingIndicator,
	args: {
		active: true
	}
} satisfies Meta<ComponentProps<typeof LoadingIndicator>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof LoadingIndicator>>;

export const Loading: Story = {
	args: {
		active: true
	}
};

export const Idle: Story = {
	args: {
		active: false
	}
};
