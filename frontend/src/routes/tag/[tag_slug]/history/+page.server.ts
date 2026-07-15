import client from '$lib/api.server';
import { HistoricalEntities } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const song_page = parseInt(url.searchParams.get('song_page') ?? '0', 10) || 1;
	const { tag: tag } = await parent();

	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: HistoricalEntities.tagwork,
				id: params.tag_slug,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	if (tag.song) {
		const { data: song_history } = await client.GET('/api/history/history', {
			fetch,
			params: {
				query: {
					entity: HistoricalEntities.mediasong,
					id: tag.song.id,
					limit: batch_size,
					offset: (song_page - 1) * batch_size
				}
			}
		});

		return {
			history,
			song_history,
			batch_size
		};
	} else {
		return {
			history,
			song_history: null,
			batch_size
		};
	}
};
