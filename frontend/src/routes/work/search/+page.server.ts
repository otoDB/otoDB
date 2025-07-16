import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const tags = url.searchParams.get('tags') ?? '';
	const { data } = await client.GET('/api/work/search', {
		fetch,
		params: { query: { query: query, tags: tags, limit: batch_size, offset: 0 } }
	});
	return {
		query: query,
		query_tags: tags,
		results: data,
		batch_size
	};
};
