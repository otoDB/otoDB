import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data: comments } = await client.GET('/api/comment/recent', {
		params: { query: { limit: batch_size, offset: (page - 1) * batch_size } },
		fetch
	});
	return { comments, page, batch_size };
};
