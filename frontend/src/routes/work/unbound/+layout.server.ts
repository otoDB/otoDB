import type { LayoutServerLoad } from './$types';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';

export const load: LayoutServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, UserLevel.EDITOR, url.pathname);

	return {
		links: [
			{ pathname: `work/unbound`, title: m.suave_gray_stork_type() },
			{ pathname: `work/unbound/rejected`, title: m.weird_lucky_hornet_grip() }
		]
	};
};
