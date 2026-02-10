import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch, locals, url }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER);

	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/profile/notifications', {
		fetch,
		params: { query: { limit: batch_size, offset: (page - 1) * batch_size } }
	});

	if (!data) error(500, { message: 'Internal server error' });

	return {
		notifications: data,
		batch_size,
		page,
		head: { title: m.free_keen_wren_exhale() }
	};
};
