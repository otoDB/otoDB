import client from '$lib/api.server';

import { userLevelGuard } from '$lib/route_guard';
import type { PageServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ fetch, locals, url, params }) => {
	userLevelGuard(locals.user, 'MEMBER');
	if (params.username !== locals.user?.username) redirect(303, `/profile/${params.username}`);

	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/profile/notifications', {
		fetch,
		params: { query: { limit: batch_size, offset: (page - 1) * batch_size } }
	});

	return {
		notifications: data,
		batch_size,
		page,
		head: { title: m.free_keen_wren_exhale() }
	};
};
