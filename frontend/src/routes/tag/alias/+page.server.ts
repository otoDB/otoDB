import type { PageServerLoad } from './$types';
import { userLevelGuard } from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Editor, url.pathname);
	const from = url.searchParams.get('from');
	return { from: from ? [from] : [], head: { title: m.front_maroon_hamster_urge() } };
};
