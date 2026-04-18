import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

import { userLevelGuard } from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);
	return { head: { title: m.plane_inner_chipmunk_race() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const name = data.get('name') as string,
			description = data.get('description') as string;

		const { error, data: list_id } = await client.POST('/api/list/list', {
			fetch,
			body: {
				name,
				description
			}
		});
		if (error) return fail(400, { name, description, failed: true });

		redirect(303, `/list/${list_id}`);
	}
} satisfies Actions;
