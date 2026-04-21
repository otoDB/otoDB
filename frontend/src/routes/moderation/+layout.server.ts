import type { LayoutServerLoad } from './$types';
import { Levels } from '$lib/schema';
import { hasUserLevel } from '$lib/enums/userLevel';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		links: [
			...(hasUserLevel(locals.user?.level, Levels.Editor)
				? [{ pathname: 'moderation', title: 'Queue' }]
				: []),
			{ pathname: 'moderation/history', title: 'History' }
		],
		head: {
			title: m.minor_inner_lynx_adapt()
		}
	};
};
