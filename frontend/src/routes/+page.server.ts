import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const randomWork = await Promise.all(Array(4).fill(null).map(() => client.GET('/api/work/random', { fetch })));
	if (randomWork.some(w => w.error !== undefined)) error(500, { message: 'Internal server error' });

	return {
		random: randomWork.map(w => w.data)
	};
};
