import { WikiKind } from '$lib/schema';
import client from '$lib/api.server';
import type { PageServerLoad } from './$types';

const isWikiKind = (v: string | null): v is WikiKind =>
	v === WikiKind.tag || v === WikiKind.work || v === WikiKind.docs;

export const load: PageServerLoad = async ({ url, fetch }) => {
	const batch_size = 20;
	const q = url.searchParams.get('q') ?? undefined;
	const kindParam = url.searchParams.get('kind');
	const kind = isWikiKind(kindParam) ? kindParam : undefined;
	const page = parseInt(url.searchParams.get('page') ?? '1', 10) || 1;

	const { data } = await client.GET('/api/wiki/', {
		fetch,
		params: {
			query: {
				q,
				kind,
				limit: batch_size,
				offset: batch_size * (page - 1)
			}
		}
	});

	return {
		q: q ?? '',
		kind: kind ?? '',
		page,
		batch_size,
		results: data ?? { items: [], count: 0 }
	};
};
