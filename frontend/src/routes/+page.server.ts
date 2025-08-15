import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const [randomWork, recentWork, recentChanges] = await Promise.all([
		client.GET('/api/work/random', {
			fetch,
			params: { query: { n: 8 } }
		}),
		client.GET('/api/work/recent', {
			fetch,
			params: { query: { n: 8 } }
		}),
		client.GET('/api/history/recent', {
			fetch,
			params: { query: { limit: 8, offset: 0 } }
		})
	]);
	if (randomWork.error || recentWork.error || recentChanges.error)
		error(500, { message: 'Internal server error' });

	return {
		random: randomWork.data,
		recent: recentWork.data,
		changes: recentChanges.data.items
	};
};
