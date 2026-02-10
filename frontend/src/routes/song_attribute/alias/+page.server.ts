import { UserLevel } from '$lib/enums';
import type { PageServerLoad } from '../../work/unbound/$types';
import userLevelGuard from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, UserLevel.EDITOR, url.pathname);
	const from = url.searchParams.get('from');
	return { from: from ? [from] : [], head: { title: m.fine_maroon_seal_flip() } };
};
