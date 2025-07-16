import client from '$lib/api';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, locals }) => {
	const stats = await client.GET('/api/stats', { fetch });

	return {
		user: locals.user,
		stats: stats.data
	};
};
