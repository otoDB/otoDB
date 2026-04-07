import { redirect } from '@sveltejs/kit';
import { UserLevel } from './enums';
import { hasUserLevel, resolveUserLevelById, UserLevel as UserLevel2 } from './enums/UserLevel';

/**
 * @deprecated
 */
export const userLevelCheck = (user: App.Locals['user'], userLevel = UserLevel.MEMBER) => {
	return !user || user.level < userLevel;
};

export const userLevelGuard = (
	user: App.Locals['user'],
	userLevel: keyof typeof UserLevel2,
	from: string | null = null,
	to = '/login'
) => {
	if (!user || hasUserLevel(resolveUserLevelById(user.level), userLevel))
		redirect(303, to === '/login' && from ? `${to}?from=${from}` : to);
};
