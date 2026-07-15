import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import WorkThumbnail from './WorkThumbnail.svelte';

const meta = {
	component: WorkThumbnail,
	args: {
		alt: 'Work thumbnail',
		class: 'w-64 h-48'
	}
} satisfies Meta<ComponentProps<typeof WorkThumbnail>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof WorkThumbnail>>;

export const WithImage: Story = {
	args: { thumbnail: '/storybook-static/thumbnail_1280x720.jpg' }
};

export const NoImage: Story = {
	args: { thumbnail: null }
};

export const UndefinedThumbnail: Story = {
	args: { thumbnail: undefined }
};
