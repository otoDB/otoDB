import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const category = parseInt(url.searchParams.get('category') ?? '-1', 10);
	const media_type = (url.searchParams.getAll('media_type') as string[]).map((s) => +s);
	const { data } = await client.GET('/api/tag/search', {
		fetch,
		params: { query: { query: query, limit: batch_size, offset: 0, category, media_type } }
	});
	return {
		query,
		category,
		results: data,
		batch_size,
		media_type
	};
};
