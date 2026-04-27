import client from '$lib/api.server';

import { userLevelGuard } from '$lib/route_guard';
import type { PageServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';
import { redirect } from '@sveltejs/kit';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, locals, url, params }) => {
	userLevelGuard(locals.user, Levels.Member);
	if (params.username !== locals.user?.username) redirect(303, `/profile/${params.username}`);

	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const sub_page = parseInt(url.searchParams.get('sub_page') ?? '0', 10) || 1;

	const [nonsub, sub] = await Promise.all([
		client.GET('/api/profile/notifications', {
			fetch,
			params: {
				query: {
					subscription: false,
					limit: batch_size,
					offset: (page - 1) * batch_size
				}
			}
		}),
		client.GET('/api/profile/notifications', {
			fetch,
			params: {
				query: {
					subscription: true,
					limit: batch_size,
					offset: (sub_page - 1) * batch_size
				}
			}
		})
	]);

	return {
		nonsub_notifications: nonsub.data,
		sub_notifications: sub.data,
		batch_size,
		page,
		sub_page,
		head: { title: m.free_keen_wren_exhale() }
	};
};
