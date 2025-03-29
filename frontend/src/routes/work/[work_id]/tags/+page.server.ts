import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import type { PageServerLoad } from '../$types';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ fetch, params, locals, parent, url }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);

	const tags = (await parent()).tags;
	const { data: scores } = await client.GET('/api/work/tag_scores', {
		fetch,
		params: { query: { work_id: +params.work_id } }
	});
	tags.forEach((tag, i) => {
		tags[i] = { ...tags[i], ...scores?.find((e) => e.tag_slug === tag.slug) };
	});
	return { tags };
};
