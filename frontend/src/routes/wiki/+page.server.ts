import client from '$lib/api.server';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const q = url.searchParams.get('q') ?? undefined;
	const page = parseInt(url.searchParams.get('page') ?? '1', 10) || 1;

	const { data } = await client.GET('/api/wiki/', {
		fetch,
		params: {
			query: {
				q,
				limit: batch_size,
				offset: batch_size * (page - 1)
			}
		}
	});

	return {
		q: q ?? '',
		page,
		batch_size,
		results: data ?? { items: [], count: 0 }
	};
};
