import client from '$lib/api';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, locals }) => {
	const { data: stats } = await client.GET('/api/stats', { fetch });

	return {
		user: locals.user,
		stats: {
			works: stats[0] as number,
			tags: stats[1] as number,
			songs: stats[2] as number,
			lists: stats[3] as number
		}
	};
};
