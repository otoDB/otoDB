import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const { data } = await client.GET('/api/post/categories', {
		fetch
	});
	return { categories: data! };
};
