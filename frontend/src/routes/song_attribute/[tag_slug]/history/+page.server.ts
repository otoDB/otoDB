import client from '$lib/api.server';
import { HistoricalEntities } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, parent }) => {
	const { tag } = await parent();

	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: HistoricalEntities.tagsong,
				id: tag.id
			}
		}
	});

	return {
		history
	};
};
