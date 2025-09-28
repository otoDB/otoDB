import client from '$lib/api';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	const { data: comments } = await client.GET('/api/comment/comments', {
		fetch,
		params: { query: { model: 'post', pk: +params.post_id } }
	});
	return { comments };
};
