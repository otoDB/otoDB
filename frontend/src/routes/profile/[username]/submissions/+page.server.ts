import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params, url }) => {
	const batch_size = 80;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data: submissions } = await client.GET('/api/profile/submissions', {
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
		submissions,
		page,
		batch_size
	};
};
