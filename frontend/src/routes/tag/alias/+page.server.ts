import { UserLevel } from '$lib/enums';
import type { PageServerLoad } from '../../work/unbound/$types';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, UserLevel.MODERATOR, url.pathname);
};
