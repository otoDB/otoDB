import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const batch_size = 20;
	const { data: submissions } = await client.GET('/api/profile/submissions', {
		fetch,
		params: {
			query: {
				username: params.username,
				limit: batch_size,
				offset: 0,
			}
		}
	});
	return {
		submissions,
		batch_size
	};
};
