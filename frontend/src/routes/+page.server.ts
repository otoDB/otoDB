import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const randomWork = await client.GET('/api/work/random', { fetch, params: { query: { n: 4 } } });
	if (randomWork.error) error(500, { message: 'Internal server error' });

	return {
		random: randomWork.data
	};
};
