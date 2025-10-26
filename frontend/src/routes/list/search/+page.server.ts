import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/list/search', {
		fetch,
		params: { query: { query: query, limit: batch_size, offset: (page - 1) * batch_size } }
	});
	return {
		query: query,
		results: data,
		batch_size,
		page
	};
};
