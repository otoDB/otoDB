import type { Meta, StoryObj } from '@storybook/sveltekit';
import { http, HttpResponse } from 'msw';
import type { ComponentProps } from 'svelte';
import { Levels, ThemePref, VideoPlatformPref } from '$lib/schema';
import Page from './+page.svelte';

const handlers = [http.post('*/api/user/prefs', () => new HttpResponse(null, { status: 200 }))];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const loggedInUser = {
	csrf: 'csrf-token',
	user_id: '1',
	username: 'member_user',
	level: Levels.Member,
	prefs: {
		THEME: ThemePref.Plain_Light,
		VIDEO_PLATFORM: VideoPlatformPref.Auto,
		PREFER_AUTHOR_UPLOAD: false
	},
	notifs_count: 0,
	notifs_nonsub_count: 0
};

const meta = {
	component: Page,
	args: {
		data: { user: null, stats }
	},
	parameters: {
		msw: { handlers }
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

export const Guest: Story = {};

export const LoggedIn: Story = {
	args: {
		data: { user: loggedInUser, stats }
	}
};

export const LoggedInWithVideoPlatform: Story = {
	args: {
		data: {
			user: {
				...loggedInUser,
				prefs: {
					...loggedInUser.prefs,
					VIDEO_PLATFORM: VideoPlatformPref.YouTube,
					PREFER_AUTHOR_UPLOAD: true
				}
			},
			stats
		}
	}
};
