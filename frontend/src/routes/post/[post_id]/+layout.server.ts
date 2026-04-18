import type { LayoutServerLoad } from './$types';
import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages.js';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	const { data } = await client.GET('/api/post/post', {
		fetch,
		params: { query: { post_id: +params.post_id } }
	});
	return {
		post: data,
		post_id: params.post_id,
		head: {
			title: data.title,
			ogType: 'article',
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.just_salty_anaconda_nourish(), url: '/post/overview' },
				{ name: data.title, url: `/post/${params.post_id}` }
			]
		}
	};
};
