import client from '$lib/api.server';
import { PostEntities } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/post/threads', {
		fetch,
		params: {
			query: {
				entity: PostEntities.tagwork,
				id: params.tag_slug,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	return {
		threads: data,
		batch_size,
		page
	};
};
