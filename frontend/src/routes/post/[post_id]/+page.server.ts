import client, { commentClient } from '$lib/api';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, params }) => {
	const comments = await commentClient.GET('post', +params.post_id, fetch);
	return { comments };
};
