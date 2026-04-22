import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { Levels } from '$lib/schema';
import { userLevelGuard } from '$lib/route_guard';

export const load: PageServerLoad = async ({ fetch, params, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const sourceId = +params.source_id;
	if (isNaN(sourceId)) {
		const { error } = await import('@sveltejs/kit');
		error(400, { message: 'Bad request' });
	}

	const [{ data: source }, { data: events }] = await Promise.all([
		client.GET('/api/upload/source', {
			fetch,
			params: { query: { source_id: sourceId } }
		}),
		client.GET('/api/moderation/events', {
			fetch,
			params: { query: { source_id: sourceId } }
		})
	]);

	return {
		source,
		events,
		head: {
			title: `Moderation: Source #${sourceId}`
		}
	};
};
