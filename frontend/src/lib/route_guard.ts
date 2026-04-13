import { redirect } from '@sveltejs/kit';
import { hasUserLevelOld, UserLevel } from './enums/UserLevel';

export const userLevelGuard = (
	user: App.Locals['user'],
	userLevel: keyof typeof UserLevel,
	from: string | null = null,
	to = '/login'
): user is Exclude<App.Locals['user'], null> => {
	if (!hasUserLevelOld(user?.level, userLevel))
		redirect(303, to === '/login' && from ? `${to}?from=${from}` : to);
	return true;
};
