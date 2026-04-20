import type { PageServerLoad } from '../$types';
import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);
};
