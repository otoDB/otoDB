import client from '$lib/api.server';
import { HistoricalEntities } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: HistoricalEntities.mediawork,
				id: params.work_id,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	return {
		history,
		batch_size
	};
};
