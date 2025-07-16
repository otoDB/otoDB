import { redirect } from '@sveltejs/kit';
import { UserLevel } from './enums';

export const userLevelCheck = (user: App.Locals['user'], userLevel = UserLevel.MEMBER) => {
	return !user || user.level < userLevel;
};

const userLevelGuard = (
	user: App.Locals['user'],
	userLevel = UserLevel.MEMBER,
	from: string | null = null,
	to = '/login'
) => {
	if (userLevelCheck(user, userLevel))
		redirect(303, to === '/login' && from ? `${to}?from=${from}` : to);
};

export default userLevelGuard;
