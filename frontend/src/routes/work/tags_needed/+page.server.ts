import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const { data } = await client.GET('/api/work/tags_needed', {
		fetch,
		params: { query: { limit: batch_size, offset: 0 } }
	});
	return {
		results: data,
		batch_size
	};
};
