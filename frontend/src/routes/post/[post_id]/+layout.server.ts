import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import client from '$lib/api';
import { m } from '$lib/paraglide/messages.js';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	if (isNaN(+params.post_id)) error(400, { message: 'Bad request' });
	const { data, error: e } = await client.GET('/api/post/post', {
		fetch,
		params: { query: { post_id: +params.post_id } }
	});
	if (e) error(404, { message: 'Not found' });
	return {
		post: data,
		post_id: params.post_id,
		head: {
			title: data.title,
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.just_salty_anaconda_nourish(), url: '/post/overview' },
				{ name: data.title, url: `/post/${params.post_id}` }
			]
		}
	};
};
