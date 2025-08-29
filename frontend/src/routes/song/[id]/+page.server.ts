import client from '$lib/api';
import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const { data, error: e } = await client.GET('/api/tag/song', {
		fetch,
		params: { query: { id: +params.id } }
	});
	if (e) error(404, { message: 'Not found' });

	redirect(303, `/tag/${encodeURIComponent(data)}`);
};
