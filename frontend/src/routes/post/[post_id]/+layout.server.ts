import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import client from '$lib/api';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	if (isNaN(+params.post_id)) error(400, { message: 'Bad request' });
	const { data, error: e } = await client.GET('/api/post/post', {
		fetch,
		params: { query: { post_id: +params.post_id } }
	});
	if (e) error(404, { message: 'Not found' });
	return { post: data, post_id: params.post_id };
};
