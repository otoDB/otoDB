import type { PageServerLoad } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ fetch, locals, url }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);

	const page = +(url.searchParams.get('page') || '1');
	const userId = url.searchParams.get('user_id') ? +url.searchParams.get('user_id')! : undefined;

	const { data: events } = await client.GET('/api/moderation/events', {
		fetch,
		params: {
			query: {
				...(userId ? { user_id: userId } : {}),
				limit: 30,
				offset: (page - 1) * 30
			}
		}
	});

	return {
		events,
		page,
		batchSize: 30,
		userId,
		isEditor: (locals.user?.level ?? 0) >= UserLevel.EDITOR
	};
};
