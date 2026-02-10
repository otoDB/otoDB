import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch, setHeaders, locals }) => {
	if (!locals.user) {
		setHeaders({
			'Cache-Control': 'public, s-maxage=600, max-age=0',
			Vary: 'Accept-Language'
		});
	}

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
		posts: posts.data,
		head: {
			title: m.fine_late_chicken_quiz(),
			description: m.mild_loud_shad_enchant({
				type: 'otoDB',
				name: m.glad_born_mouse_taste()
			})
		}
	};
};
