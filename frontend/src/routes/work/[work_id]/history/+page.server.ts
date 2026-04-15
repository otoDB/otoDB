import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: 'mediawork',
				id: +params.work_id
			}
		}
	});

	if (!history) error(500, { message: 'Failed to load history' });

	return {
		history
	};
};
