import type { Meta, StoryObj } from '@storybook/sveltekit';
import type { ComponentProps } from 'svelte';
import { m } from '$lib/paraglide/messages.js';
import {
	Levels,
	PathsApiUserSearchGetParametersQueryOrder as OrderEnum,
	type components
} from '$lib/schema';
import Page from './+page.svelte';

type ProfileIndex = components['schemas']['ProfileIndexSchema'];

const stats = { works: 1234, tags: 567, songs: 89, lists: 42 };

const head = { title: m.bright_nimble_eagle_glide() };

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

const batch_size = 30;

// The register holds a few hundred accounts, so a search without filters always
// fills a batch and always renders the pager.
const total_count = 243;

// Accounts are placeholders named after their id. Only the shape of the data —
// how many rows come back, how the levels are distributed, how wide the counts
// spread — is modelled on the live listing.
const profile = (
	id: number,
	level: Levels,
	[works_count, revisions_count, posts_count, comments_count]: [number, number, number, number],
	date_created: string
): ProfileIndex => ({
	id: `${id}`,
	username: `user${id}`,
	level,
	works_count,
	revisions_count,
	posts_count,
	comments_count,
	date_created
});

// Ordered by `-date_created`, the default. Recent sign-ups have barely any
// activity behind them, which is what the first page of the listing looks like
// in practice; the few accounts with real numbers are scattered through it.
const newestFirst: ProfileIndex[] = [
	profile(243, Levels.Member, [0, 0, 0, 0], '2026-08-06T21:35:58Z'),
	profile(242, Levels.Member, [1, 7, 0, 0], '2026-07-30T05:16:18Z'),
	profile(241, Levels.Member, [0, 0, 0, 0], '2026-07-29T21:14:29Z'),
	profile(240, Levels.Member, [1, 4, 0, 0], '2026-07-28T14:02:18Z'),
	profile(239, Levels.Member, [0, 2, 0, 0], '2026-07-28T10:01:08Z'),
	profile(238, Levels.Member, [0, 0, 0, 0], '2026-07-26T03:44:51Z'),
	profile(237, Levels.Member, [3, 11, 0, 1], '2026-07-24T18:20:02Z'),
	profile(236, Levels.Member, [0, 0, 0, 0], '2026-07-21T07:55:37Z'),
	profile(235, Levels.Restricted, [0, 0, 0, 0], '2026-07-19T22:13:09Z'),
	profile(234, Levels.Member, [12, 48, 0, 2], '2026-07-17T11:38:44Z'),
	profile(233, Levels.Member, [0, 1, 0, 0], '2026-07-15T09:02:26Z'),
	profile(232, Levels.Member, [980, 7282, 2, 1], '2026-07-12T10:34:09Z'),
	profile(231, Levels.Member, [0, 0, 0, 0], '2026-07-10T16:47:31Z'),
	profile(230, Levels.Member, [5, 19, 1, 0], '2026-07-08T04:29:57Z'),
	profile(229, Levels.Member, [0, 0, 0, 0], '2026-07-05T13:11:40Z'),
	profile(228, Levels.Member, [2, 6, 0, 3], '2026-07-03T20:05:12Z'),
	profile(227, Levels.Member, [0, 0, 0, 0], '2026-07-01T08:53:24Z'),
	profile(226, Levels.Editor, [1460, 4494, 1, 42], '2026-06-28T03:08:04Z'),
	profile(225, Levels.Member, [0, 0, 0, 0], '2026-06-26T15:36:48Z'),
	profile(224, Levels.Member, [24, 133, 0, 5], '2026-06-24T02:18:33Z'),
	profile(223, Levels.Member, [0, 0, 0, 0], '2026-06-21T19:41:07Z'),
	profile(222, Levels.Editor, [1040, 3828, 0, 3], '2026-06-19T01:28:33Z'),
	profile(221, Levels.Restricted, [0, 0, 0, 0], '2026-06-17T12:07:19Z'),
	profile(220, Levels.Member, [8, 27, 0, 0], '2026-06-14T23:50:55Z'),
	profile(219, Levels.Member, [0, 3, 0, 1], '2026-06-12T06:34:02Z'),
	profile(218, Levels.Editor, [1377, 8798, 6, 0], '2026-06-09T23:19:23Z'),
	profile(217, Levels.Member, [0, 0, 0, 0], '2026-06-07T17:26:41Z'),
	profile(216, Levels.Member, [17, 62, 2, 4], '2026-06-05T10:12:58Z'),
	profile(215, Levels.Member, [0, 0, 0, 0], '2026-06-03T05:44:16Z'),
	profile(214, Levels.Mod, [1023, 4648, 22, 1], '2026-06-01T01:23:27Z')
];

// The same listing re-sorted by `-works_count`, so the sort arrow moves to
// another column and the table fills up with the heaviest contributors.
const byWorksCount: ProfileIndex[] = [
	profile(187, Levels.Mod, [2431, 2552, 17, 134], '2025-07-15T19:56:52Z'),
	profile(203, Levels.Mod, [2353, 10672, 60, 45], '2025-10-23T12:34:20Z'),
	profile(209, Levels.Editor, [2047, 16097, 10, 21], '2026-02-12T02:42:12Z'),
	profile(206, Levels.Editor, [1493, 11421, 30, 5], '2026-01-11T03:28:24Z'),
	profile(226, Levels.Editor, [1460, 4494, 1, 42], '2026-06-28T03:08:04Z'),
	profile(174, Levels.Admin, [1414, 788, 11, 26], '2025-05-22T12:32:32Z'),
	profile(218, Levels.Editor, [1377, 8798, 6, 0], '2026-06-09T23:19:23Z'),
	profile(207, Levels.Editor, [1336, 13377, 2, 65], '2026-01-11T03:54:27Z'),
	profile(222, Levels.Editor, [1040, 3828, 0, 3], '2026-06-19T01:28:33Z'),
	profile(214, Levels.Mod, [1023, 4648, 22, 1], '2026-06-01T01:23:27Z'),
	profile(232, Levels.Member, [980, 7282, 2, 1], '2026-07-12T10:34:09Z'),
	profile(168, Levels.Admin, [864, 6431, 49, 12], '2025-03-19T22:53:12Z'),
	profile(183, Levels.Editor, [742, 3190, 8, 30], '2025-06-28T14:09:44Z'),
	profile(211, Levels.Member, [688, 2044, 3, 9], '2026-03-02T09:17:35Z'),
	profile(195, Levels.Editor, [604, 5527, 14, 18], '2025-08-30T21:02:51Z'),
	profile(204, Levels.Member, [571, 1832, 0, 7], '2025-11-11T04:48:20Z'),
	profile(178, Levels.Mod, [498, 2971, 26, 63], '2025-06-04T16:25:13Z'),
	profile(212, Levels.Member, [463, 1204, 1, 2], '2026-03-19T11:33:07Z'),
	profile(186, Levels.Editor, [431, 3688, 5, 11], '2025-07-09T08:40:29Z'),
	profile(205, Levels.Member, [402, 977, 0, 0], '2025-12-24T13:56:38Z'),
	profile(199, Levels.Member, [377, 1450, 2, 15], '2025-10-05T18:21:46Z'),
	profile(210, Levels.Member, [341, 862, 0, 4], '2026-02-27T07:14:52Z'),
	profile(191, Levels.Member, [318, 1103, 7, 22], '2025-08-14T22:37:05Z'),
	profile(201, Levels.Member, [295, 744, 0, 1], '2025-12-02T03:29:18Z'),
	profile(184, Levels.Member, [271, 1918, 4, 8], '2025-06-30T12:50:41Z'),
	profile(196, Levels.Member, [244, 655, 1, 0], '2025-09-17T20:06:24Z'),
	profile(179, Levels.Member, [219, 1370, 0, 6], '2025-06-11T05:43:59Z'),
	profile(175, Levels.Member, [188, 509, 3, 13], '2025-05-29T10:31:16Z'),
	profile(224, Levels.Member, [24, 133, 0, 5], '2026-06-24T02:18:33Z'),
	profile(216, Levels.Member, [17, 62, 2, 4], '2026-06-05T10:12:58Z')
];

// `username` is a case-insensitive substring filter, so `19` pulls in `user19`
// along with every `user19x`.
const matching19: ProfileIndex[] = [
	profile(199, Levels.Member, [377, 1450, 2, 15], '2025-10-05T18:21:46Z'),
	profile(196, Levels.Member, [244, 655, 1, 0], '2025-09-17T20:06:24Z'),
	profile(195, Levels.Editor, [604, 5527, 14, 18], '2025-08-30T21:02:51Z'),
	profile(192, Levels.Member, [0, 0, 0, 0], '2025-08-22T05:11:30Z'),
	profile(191, Levels.Member, [318, 1103, 7, 22], '2025-08-14T22:37:05Z'),
	profile(190, Levels.Restricted, [0, 0, 0, 0], '2025-08-09T14:02:17Z'),
	profile(19, Levels.Member, [46, 180, 1, 2], '2025-01-27T06:48:33Z')
];

const editors = byWorksCount.filter((p) => p.level === Levels.Editor);

const baseData = {
	stats,
	head,
	user: memberUser,
	batch_size,
	username: '',
	level: null,
	order: OrderEnum.ValueMinusdate_created,
	results: { items: newestFirst, count: total_count }
};

const meta = {
	component: Page,
	args: { data: baseData }
} satisfies Meta<ComponentProps<typeof Page>>;

export default meta;
type Story = StoryObj<ComponentProps<typeof Page>>;

/** An unfiltered search: a full batch sorted newest-first, with the pager below. */
export const Default: Story = {};

/** Re-sorted by work count, which moves the sort arrow off the join date column. */
export const SortedByWorksCount: Story = {
	args: {
		data: {
			...baseData,
			order: OrderEnum.ValueMinusworks_count,
			results: { items: byWorksCount, count: total_count }
		}
	}
};

/** A username substring search, narrow enough that the result fits on one page. */
export const FilteredByUsername: Story = {
	args: {
		data: {
			...baseData,
			username: '19',
			results: { items: matching19, count: matching19.length }
		}
	}
};

/** Filtered to editors, so the level select renders with a value selected. */
export const FilteredByLevel: Story = {
	args: {
		data: {
			...baseData,
			level: Levels.Editor,
			order: OrderEnum.ValueMinusworks_count,
			results: { items: editors, count: editors.length }
		}
	}
};
