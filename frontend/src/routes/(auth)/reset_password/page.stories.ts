import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels } from '$lib/schema';
import type { ActionData } from './$types';
import Page from './+page.svelte';

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = { title: m.true_tough_butterfly_sew() };

const loggedInMember = {
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

const baseData = {
	user: null,
	stats,
	head,
	token: undefined
};

const requestSuccessForm = { success: true } as ActionData;
const resetSuccessForm = { reset_success: true } as ActionData;

const meta = {
	component: Page,
	args: {
		data: baseData,
		form: undefined
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

// Anonymous visitor without a `?token=` query param: request-reset form.
export const RequestEmail: Story = {};

// After submitting the request-reset form successfully.
export const RequestSuccess: Story = {
	args: {
		data: baseData,
		form: requestSuccessForm
	}
};

// Anonymous visitor who followed the reset link (`?token=...`): new-password form.
export const TokenReset: Story = {
	args: {
		data: { ...baseData, token: 'sample-reset-token' },
		form: undefined
	}
};

// Already logged-in user resetting their own password (no token, but `data.user` is set).
export const LoggedInReset: Story = {
	args: {
		data: { ...baseData, user: loggedInMember },
		form: undefined
	}
};

// After submitting the new-password form successfully.
export const ResetSuccess: Story = {
	args: {
		data: { ...baseData, token: 'sample-reset-token' },
		form: resetSuccessForm
	}
};
