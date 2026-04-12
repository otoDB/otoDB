import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const query = url.searchParams.get('query') ?? '';
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/list/search', {
		fetch,
		params: { query: { query: query, limit: batch_size, offset: (page - 1) * batch_size } }
	});
	return {
		query: query,
		results: data,
		batch_size,
		page,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.mean_top_antelope_love(),
				name: m.stale_loose_squid_cut()
			})
		}
	};
};
