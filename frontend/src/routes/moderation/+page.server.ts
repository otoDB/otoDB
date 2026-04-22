import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { userLevelGuard } from '$lib/route_guard';
import { Levels, ModQueueCategory } from '$lib/schema';

const tabToCategory: Record<string, ModQueueCategory | undefined> = {
	pending: ModQueueCategory.Pending,
	flagged: ModQueueCategory.Flagged,
	appealed: ModQueueCategory.Appealed
};

export const load: PageServerLoad = async ({ fetch, locals, url }) => {
	userLevelGuard(locals.user, Levels.Editor, url.pathname);

	const tab = url.searchParams.get('tab') || 'all';
	const page = +(url.searchParams.get('page') || '1');

	if (tab === 'sources') {
		const { data: sources } = await client.GET('/api/upload/list', {
			fetch,
			params: { query: { is_pending: true, limit: 30, offset: (page - 1) * 30 } }
		});
		return { tab, page, sources, queue: null, batchSize: 30 };
	}

	const { data: queue } = await client.GET('/api/work/queue', {
		fetch,
		params: {
			query: {
				category: tabToCategory[tab],
				limit: 30,
				offset: (page - 1) * 30
			}
		}
	});

	return { tab, page, queue, sources: null, batchSize: 30 };
};
