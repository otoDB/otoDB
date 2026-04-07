import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/post/threads', {
		fetch,
		params: {
			query: {
				entity: 'tagwork',
				id: params.tag_slug,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});
	// TODO: properly handle fetch errors
	if (!data) error(500, 'Failed to fetch data.');
	return {
		threads: data,
		batch_size,
		page
	};
};
