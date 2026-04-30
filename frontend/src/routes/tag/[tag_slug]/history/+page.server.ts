import client from '$lib/api.server';
import { HistoricalEntities } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const { tag: tag } = await parent();

	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: HistoricalEntities.tagwork,
				id: tag.id
			}
		}
	});

	if (tag.song) {
		const { data: song_history } = await client.GET('/api/history/history', {
			fetch,
			params: {
				query: {
					entity: HistoricalEntities.mediasong,
					id: tag.song.id
				}
			}
		});

		return {
			history,
			song_history
		};
	} else {
		return {
			history,
			song_history: null
		};
	}
};
