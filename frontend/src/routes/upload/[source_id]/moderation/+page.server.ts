import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { Levels } from '$lib/schema';
import { userLevelGuard } from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch, params, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const sourceId = params.source_id;

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
			title: m.mild_loud_shad_enchant({
				type: m.minor_inner_lynx_adapt(),
				name: `${m.extra_brave_tapir_skip()} #${sourceId}`
			})
		}
	};
};
