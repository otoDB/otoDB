import type { PageServerLoad } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';

export const load: PageServerLoad = async ({ fetch, params, locals }) => {
	const { data: events } = await client.GET('/api/moderation/events', {
		fetch,
		params: { query: { work_id: +params.work_id } }
	});

	return {
		events,
		isEditor: (locals.user?.level ?? 0) >= UserLevel.EDITOR
	};
};
