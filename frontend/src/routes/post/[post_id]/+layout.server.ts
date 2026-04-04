import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import client from '$lib/api';
import { m } from '$lib/paraglide/messages.js';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	const postId = Number.parseInt(params.post_id, 10);

	if (isNaN(postId)) error(400, { message: 'Bad request' });

	const { data, error: e } = await client.GET('/api/post/post', {
		fetch,
		params: { query: { post_id: postId } }
	});

	if (e) error(404, { message: 'Not found' });

	return {
		post: data,
		post_id: postId,
		head: {
			title: data.title,
			ogType: 'article',
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.just_salty_anaconda_nourish(), url: '/post/overview' },
				{ name: data.title, url: `/post/${postId}` }
			]
		}
	};
};
