import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, locals }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER);

	const { data } = await client.GET('/api/profile/notifications', {
		fetch
	});

	return { notifications: data };
};
