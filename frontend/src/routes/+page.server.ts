import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, locals }) => {
	const [randomWork, recentWork, changes, posts] = await Promise.all([
		client.GET('/api/work/random', {
			fetch,
			params: { query: { n: 6 } }
		}),
		client.GET('/api/work/recent', {
			fetch,
			params: { query: { n: 6 } }
		}),
		client.GET('/api/history/recent', {
			fetch,
			params: { query: { limit: 8, offset: 0 } }
		}),
		client.GET('/api/post/recent', {
			fetch,
			params: { query: { limit: 8, offset: 0 } }
		})
	]);
	if (randomWork.error || recentWork.error || changes.error || posts.error)
		error(500, { message: 'Internal server error' });

	return {
		random: randomWork.data,
		recent: recentWork.data,
		changes: changes.data,
		posts: posts.data
	};
};
