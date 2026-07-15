import client from '$lib/api.server';
import { ModelsWithComments } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const data = await parent();

	const batch_size = 20;

	const [{ data: details }, { data: works }, { data: connections }, { data: comments }] =
		await Promise.all([
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
			}),
			client.GET('/api/comment/comments', {
				fetch,
				params: {
					query: {
						model: ModelsWithComments.tagwork,
						pk: data.tag.id
					}
				}
			})
		]);

	const song_relations = data.song_relations;

	const song_connections = data.tag.song
		? (
				await client.GET('/api/tag/song_connection', {
					fetch,
					params: { query: { song_id: data.tag.song.id } }
				})
			).data
		: null;

	const similar = client
		.GET('/api/tag/similar', {
			fetch,
			params: { query: { tag_slug: params.tag_slug } }
		})
		.then((res) => res.data);

	return {
		...details,
		works,
		comments,
		song_relations,
		batch_size,
		connections,
		song_connections,
		similar
	};
};
