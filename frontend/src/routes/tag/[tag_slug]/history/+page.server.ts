import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: 'tagwork',
				object_id: params.tag_slug
			}
		}
	});

	return {
		history
	};
};
