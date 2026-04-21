import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { hasUserLevel } from '$lib/enums/userLevel';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, params, locals }) => {
	const { data: events } = await client.GET('/api/moderation/events', {
		fetch,
		params: { query: { work_id: +params.work_id } }
	});

	return {
		events,
		isEditor: hasUserLevel(locals.user?.level, Levels.Editor)
	};
};
