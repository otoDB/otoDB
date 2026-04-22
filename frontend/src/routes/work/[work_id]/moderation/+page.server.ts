import type { PageServerLoad } from './$types';
import client from '$lib/api.server';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const { data: events } = await client.GET('/api/moderation/events', {
		fetch,
		params: { query: { work_id: +params.work_id } }
	});

	return {
		events
	};
};
