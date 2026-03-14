import type { LayoutServerLoad } from './$types';
import { UserLevel } from '$lib/enums';
import { userLevelCheck } from '$lib/route_guard';

export const load: LayoutServerLoad = async ({ locals }) => {
	const loggedOut = userLevelCheck(locals.user);

	return {
		links: [
			...(!loggedOut && locals.user!.level >= UserLevel.EDITOR
				? [{ pathname: 'moderation', title: 'Queue' }]
				: []),
			{ pathname: 'moderation/history', title: 'History' }
		],
		head: {
			title: 'Moderation'
		}
	};
};
