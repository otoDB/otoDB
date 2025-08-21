import { UserLevel } from '$lib/enums';
import type { PageServerLoad } from '../$types';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);
};
