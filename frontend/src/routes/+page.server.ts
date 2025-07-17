import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const randomWork = await client.GET('/api/work/random', {
		fetch,
		params: { query: { n: 12 } }
	});
	if (randomWork.error) error(500, { message: 'Internal server error' });

	const recentWork = await client.GET('/api/work/recent', {
		fetch,
		params: { query: { n: 12 } }
	});
	if (recentWork.error) error(500, { message: 'Internal server error' });

	return {
		random: randomWork.data,
		recent: recentWork.data
	};
};
