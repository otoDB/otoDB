import { userLevelGuard } from '$lib/route_guard';
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from '../$types';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, parent, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);
	const data = await parent();
	if (!data.tag.song) redirect(303, `/tag/${data.tag.slug}`);
};
