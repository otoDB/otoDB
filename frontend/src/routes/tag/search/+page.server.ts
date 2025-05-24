import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const query = url.searchParams.get('query') ?? '';
	const category = parseInt(url.searchParams.get('category') ?? '-1', 10);
	const { data } = await client.GET('/api/tag/search', {
		fetch,
		params: { query: { query: query, limit: 20, offset: 0, category } }
	});
	return {
		query,
		category,
		results: data
	};
};
