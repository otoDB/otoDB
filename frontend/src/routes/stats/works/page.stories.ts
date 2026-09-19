import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import { Levels } from '$lib/schema';
import type { WorkHistoryPoint } from '$lib/stats/history';
import Page from './+page.svelte';

const stats = { works: 19_000, tags: 4_300, songs: 8_100, lists: 260 };

const head = { title: m.proud_bold_gecko_thrive() };

const memberUser = {
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

/**
 * A 32-bit xorshift, so the fixture is the same on every open: the story is meant
 * to be usable as a visual regression baseline, which rules out `Math.random()`.
 */
const xorshift = (seed: number) => () => {
	seed ^= seed << 13;
	seed ^= seed >>> 17;
	seed ^= seed << 5;
	return (seed >>> 0) / 4_294_967_296;
};

const DAY = 24 * 60 * 60 * 1000;
const FIRST_DAY = Date.parse('2019-01-01T00:00:00Z');
const DAYS = 2738; // through 2026-06-30

/**
 * The shape the real endpoint returns: ascending, sparse (quiet days are left out),
 * and with a submission rate that climbs as the site grows.
 */
const history: WorkHistoryPoint[] = [];
const random = xorshift(20260807);
let total = 0;
for (let day = 0; day < DAYS; day++) {
	const added = Math.floor(random() * (5 + day / 150));
	if (added === 0) continue;
	total += added;
	history.push({ date: new Date(FIRST_DAY + day * DAY).toISOString().slice(0, 10), total });
}

const meta = {
	component: Page,
	args: {
		data: {
			stats,
			head,
			user: memberUser,
			history
		}
	}
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** Seven and a half years of submissions, one bar per month. */
export const Default: Story = {};
