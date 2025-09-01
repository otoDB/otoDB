import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const { data } = await client.GET('/api/request/request', {
		fetch,
		params: {
			query: {
				request_id: +params.id
			}
		}
	});

	return { ...data, ...params };
};
