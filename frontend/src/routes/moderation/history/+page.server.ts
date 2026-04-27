import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { Levels } from '$lib/schema';
import { userLevelGuard } from '$lib/route_guard';

export const load: PageServerLoad = async ({ fetch, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const page = +(url.searchParams.get('page') || '1');
	const userId = url.searchParams.get('user_id') ?? undefined;

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
		userId
	};
};
