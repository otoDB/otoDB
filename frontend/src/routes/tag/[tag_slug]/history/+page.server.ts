import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const p = await parent();

	const [{ data: history }, song_history] = await Promise.all([
		client.GET('/api/history/history', {
			fetch,
			params: {
				query: {
					entity: 'tagwork',
					id: params.tag_slug
				}
			}
		}),
		p.tag.song
			? client.GET('/api/history/history', {
					fetch,
					params: {
						query: {
							entity: 'mediasong',
							id: p.tag.song.id
						}
					}
				})
			: null
	]);

	return {
		history,
		song_history: song_history?.data
	};
};
