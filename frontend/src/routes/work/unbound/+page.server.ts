import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch }) => {
	const { data, error: e } = await client.GET('/api/work/unbound', {
		fetch,
		params: { query: { pending: true } }
	});
	if (e) error(404, { message: 'Not found' });
	return { sources: data, head: { title: m.suave_gray_stork_type() } };
};
