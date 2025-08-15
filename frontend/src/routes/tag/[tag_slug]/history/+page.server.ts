import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				model: 'tagwork',
				pk: params.tag_slug
			}
		}
	});

	return {
		history
	};
};
