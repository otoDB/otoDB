import type { PageServerLoad } from './$types';
import client from '$lib/api';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const page = +(url.searchParams.get('page') || '1');
	const unbound = url.searchParams.get('unbound');
	const pending = url.searchParams.get('pending');
	const platform = url.searchParams.get('platform');
	const batchSize = 30;

	const { data: sources } = await client.GET('/api/source/list', {
		fetch,
		params: {
			query: {
				...(unbound === 'true' ? { unbound: true } : {}),
				...(pending === 'true' ? { is_pending: true } : {}),
				...(platform ? { platform: +platform } : {}),
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
			title: 'Sources'
		}
	};
};
