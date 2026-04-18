import { redirect } from '@sveltejs/kit';
import { hasUserLevel } from './enums/UserLevel';
import type { Levels } from './schema';

export const userLevelGuard = (
	user: App.Locals['user'],
	userLevel: Levels,
	from: string | null = null,
	to = '/login'
): user is Exclude<App.Locals['user'], null> => {
	if (!hasUserLevel(user?.level, userLevel))
		redirect(303, to === '/login' && from ? `${to}?from=${from}` : to);
	return true;
};
