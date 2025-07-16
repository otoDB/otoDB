import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const { data } = await client.GET('/api/list/search', {
		fetch,
		params: { query: { query: query, limit: batch_size, offset: 0 } }
	});
	return {
		query: query,
		results: data,
		batch_size
	};
};
