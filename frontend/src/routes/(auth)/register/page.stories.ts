import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = { title: m.blue_whole_camel_type() };

const baseData = { user: null, stats, head, inviteRequired: false };

const meta = {
	component: Page,
	args: {
		data: baseData,
		form: undefined
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Default: Story = {};

export const InviteRequired: Story = {
	args: {
		data: { ...baseData, inviteRequired: true }
	}
};

export const MissingFields: Story = {
	args: {
		data: baseData,
		form: { username: 'member_user', email: 'member_user@example.com', missing: true }
	}
};

export const PasswordMismatch: Story = {
	args: {
		data: baseData,
		form: { username: 'member_user', email: 'member_user@example.com', mismatch: true }
	}
};
