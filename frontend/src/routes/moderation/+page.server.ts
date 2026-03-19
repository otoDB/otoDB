import type { PageServerLoad } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ fetch, locals, url }) => {
	userLevelGuard(locals.user, UserLevel.EDITOR, url.pathname);

	const tab = (url.searchParams.get('tab') as string) || 'all';
	const page = +(url.searchParams.get('page') || '1');

	const category = tab === 'all' ? undefined : tab;

	if (tab === 'sources') {
		const { data: sources } = await client.GET('/api/source/list', {
			fetch,
			params: { query: { is_pending: true, limit: 30, offset: (page - 1) * 30 } }
		});
		return { tab, page, sources, queue: null, batchSize: 30 };
	}

	const { data: queue } = await client.GET('/api/work/queue', {
		fetch,
		params: {
			query: {
				...(category ? { category } : {}),
				limit: 30,
				offset: (page - 1) * 30
			}
		}
	});

	return { tab, page, queue, sources: null, batchSize: 30 };
};
