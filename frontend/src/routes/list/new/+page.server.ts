import client from '$lib/api.server';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

import { userLevelGuard } from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, 'MEMBER', url.pathname);
	return { head: { title: m.plane_inner_chipmunk_race() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const name = data.get('name') as string,
			description = data.get('description') as string;
		try {
			const { data: list_id } = await client.POST('/api/list/list', {
				fetch,
				body: {
					name,
					description
				}
			});
			redirect(303, `/list/${list_id}`);
		} catch {
			return fail(400, { name, description, failed: true });
		}
	}
} satisfies Actions;
