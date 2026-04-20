import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const { data } = await client.GET('/api/post/categories', {
		fetch
	});
	return { categories: data!, head: { title: m.just_salty_anaconda_nourish() } };
};
