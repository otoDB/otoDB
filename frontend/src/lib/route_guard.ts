import { redirect } from '@sveltejs/kit';
import { UserLevel } from './enums';

const userLevelGuard = (
	user: App.Locals['user'],
	userLevel = UserLevel.MEMBER,
	from: string | null = null,
	to = '/login'
) => {
	if (!user || user.level < userLevel)
		redirect(303, to === '/login' && from ? `${to}?from=${from}` : to);
};

export default userLevelGuard;
