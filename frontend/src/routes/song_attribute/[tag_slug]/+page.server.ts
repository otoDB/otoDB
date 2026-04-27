import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { ModelsWithComments } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const data = await parent();

	const [{ data: songs }, { data: comments }] = await Promise.all([
		client.GET('/api/tag/songs', {
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
					model: ModelsWithComments.tagsong,
					pk: +data.tag.id
				}
			}
		})
	]);

	return {
		songs,
		comments
	};
};
