import client from '$lib/api';
import { commentClient } from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const data = await parent();

	const batch_size = 20;

	const [{ data: details }, { data: works }, { data: connections }] = await Promise.all([
		client.GET('/api/tag/details', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/tag/works', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug,
					limit: batch_size,
					offset: 0
				}
			}
		}),
		client.GET('/api/tag/connection', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		})
	]);

	const comments = await commentClient.GET('tagwork', data.tag.id, fetch);

	const song_relations = data.song_relations;

	const song_connections = data.tag.song
		? (
				await client.GET('/api/tag/song_connection', {
					fetch,
					params: { query: { song_id: data.tag.song.id } }
				})
			).data
		: null;

	return {
		...details,
		works,
		comments,
		song_relations,
		batch_size,
		connections,
		song_connections
	};
};
