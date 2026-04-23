import type { LayoutServerLoad } from './$types';
import { Levels } from '$lib/schema';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		links: [
			...(hasUserLevel(locals.user?.level, Levels.Editor)
				? [{ pathname: 'moderation', title: m.direct_fluffy_finch_believe() }]
				: []),
			{ pathname: 'moderation/history', title: m.giant_away_scallop_hike() }
		],
		head: {
			title: m.minor_inner_lynx_adapt()
		}
	};
};
