import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params, url }) => {
	const batch_size = 30;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data: revisions } = await client.GET('/api/history/recent', {
		fetch,
		params: {
			query: {
				username: params.username,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});
	return {
		revisions,
		page,
		batch_size
	};
};
