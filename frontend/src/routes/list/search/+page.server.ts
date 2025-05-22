import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const query = url.searchParams.get('query') ?? '';
	const { data } = await client.GET('/api/list/search', {
		fetch,
		params: { query: { query: query, limit: 20, offset: 0 } }
	});
	return {
		query: query,
		results: data
	};
};
