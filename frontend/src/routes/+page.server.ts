import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const [randomWork, recentWork] = await Promise.all([
		client.GET('/api/work/random', {
			fetch,
			params: { query: { n: 8 } }
		}),
		client.GET('/api/work/recent', {
			fetch,
			params: { query: { n: 8 } }
		})
	]);
	if (randomWork.error || recentWork.error) error(500, { message: 'Internal server error' });

	return {
		random: randomWork.data,
		recent: recentWork.data
	};
};
