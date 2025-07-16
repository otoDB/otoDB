import client, { commentClient } from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const batch_size = 20;
	const [comments, { data: pending_items }] = await Promise.all([
		commentClient.GET('pool', +params.list_id, fetch),
		client.GET('/api/list/pending', {
			fetch,
			params: { query: { list_id: +params.list_id, limit: batch_size, offset: 0 } }
		})
	]);
	return { comments, pending_items };
};
