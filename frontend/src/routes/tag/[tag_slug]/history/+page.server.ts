import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { PathsApiHistoryHistoryGetParametersQueryEntity } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const { tag: tag } = await parent();

	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: PathsApiHistoryHistoryGetParametersQueryEntity.tagwork,
				id: params.tag_slug
			}
		}
	});

	if (!history) error(500, 'Failed to load history');

	if (tag.song) {
		const { data: song_history } = await client.GET('/api/history/history', {
			fetch,
			params: {
				query: {
					entity: PathsApiHistoryHistoryGetParametersQueryEntity.mediasong,
					id: tag.song.id
				}
			}
		});
		if (!song_history) error(500, 'Failed to load song history');

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
