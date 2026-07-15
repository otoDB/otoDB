import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { ErrorCode } from '$lib/schema';
import Page from './+page.svelte';

const handlers = [http.post('*/api/auth/login', () => HttpResponse.json({}))];

const meta = {
	component: Page,
	args: {
		form: undefined
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Default: Story = {};

// Mirrors the `fail(400, { username, missing: true })` branch in `+page.server.ts`'s
// `actions.default`, which the page's own `$effect` turns into an "All fields are
// required." toast.
export const MissingFields: Story = {
	args: {
		form: { username: 'member_user', missing: true }
	}
};

// Mirrors the `apiFail(apiError, { username })` branch (e.g. a `Login_Failed` API
// error). The page does not render or toast this shape directly today, so this story
// intentionally looks identical to `Default` visually — it exists to document/lock in
// the actual `form` shape the server action returns on a failed login attempt.
export const LoginFailed: Story = {
	args: {
		form: {
			failed: true,
			code: ErrorCode.Login_Failed,
			errorData: {},
			username: 'member_user'
		}
	}
};
