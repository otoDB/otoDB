import client, { commentClient } from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	if (isNaN(+params.post_id)) error(400, { message: 'Bad request' });
	const { data, error: e } = await client.GET('/api/post/post', {
		fetch,
		params: { query: { post_id: +params.post_id } }
	});
	if (e) error(404, { message: 'Not found' });
	const comments = await commentClient.GET('post', +params.post_id, fetch);
	return { post: data, comments, post_id: params.post_id };
};
