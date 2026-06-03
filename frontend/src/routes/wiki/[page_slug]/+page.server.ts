import client from '$lib/api.server';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data } = await client.GET('/api/wiki/{page_slug}', {
		fetch,
		params: { path: { page_slug: params.page_slug } }
	});

	return {
		page_slug: params.page_slug,
		wiki_page: data
	};
};
