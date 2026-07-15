import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import Footer from './Footer.svelte';

const handlers = [http.post('*/api/profile/prefs', () => new HttpResponse(null, { status: 200 }))];

const meta = {
	component: Footer,
	args: {
		user: null
	},
	parameters: {
		msw: { handlers }
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
