import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const page = +(url.searchParams.get('page') || '1');
	const unbound = url.searchParams.get('unbound');
	const pending = url.searchParams.get('pending');
	const platform = url.searchParams.get('platform');
	const batchSize = 30;

	const { data: sources } = await client.GET('/api/upload/list', {
		fetch,
		params: {
			query: {
				unbound: unbound === 'true' || undefined,
				is_pending: pending === 'true' || undefined,
				platform: platform ? +platform : undefined,
				limit: batchSize,
				offset: (page - 1) * batchSize
			}
		}
	});

	return {
		sources,
		page,
		batchSize,
		filters: { unbound, pending, platform },
		head: {
			title: m.extra_brave_tapir_skip()
		}
	};
};
