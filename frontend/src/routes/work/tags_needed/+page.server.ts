import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const batch_size = 20;
	const { data } = await client.GET('/api/work/tags_needed', {
		fetch,
		params: { query: { limit: batch_size, offset: 0 } }
	});
	return {
		results: data,
		batch_size,
		head: { title: m.spry_late_kudu_assure() }
	};
};
