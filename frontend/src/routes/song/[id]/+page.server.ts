import client from '$lib/api.server';
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const { data } = await client.GET('/api/tag/song', {
		fetch,
		params: { query: { id: +params.id } }
	});

	redirect(303, `/tag/${encodeURIComponent(data)}`);
};
