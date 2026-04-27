import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, params, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const { data: suggestions } = await client.GET('/api/work/tag_suggestions', {
		fetch,
		params: { query: { work_id: params.work_id } }
	});

	if (suggestions) {
		suggestions.creator_tags = suggestions.creator_tags.filter(
			(t) =>
				!suggestions.new_tags.find((tt) => t.slug === tt.slug) &&
				!suggestions.source_tags.find((tt) => t.slug === tt.slug)
		);
	}

	return { suggestions };
};
