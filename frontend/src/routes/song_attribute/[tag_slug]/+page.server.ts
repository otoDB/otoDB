import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { ModelsWithComments } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, parent, url }) => {
	const data = await parent();

	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;

	const [{ data: songs }, { data: comments }] = await Promise.all([
		client.GET('/api/tag/songs', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug,
					limit: batch_size,
					offset: (page - 1) * batch_size
				}
			}
		}),
		client.GET('/api/comment/comments', {
			fetch,
			params: {
				query: {
					model: ModelsWithComments.tagsong,
					pk: data.tag.id
				}
			}
		})
	]);

	return {
		songs,
		comments,
		batch_size
	};
};
