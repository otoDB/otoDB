import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import { userLevelGuard } from '$lib/route_guard';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, 'EDITOR', url.pathname);
	return { head: { title: m.heroic_same_wasp_conquer() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();

		const A = data.get('A') as string,
			B = data.get('B') as string,
			title = data.get('title') as string,
			description = data.get('description') as string,
			thumbnail_source_id = data.get('thumbnail_source_id') as string,
			rating = data.get('rating') as string;

		if (!A || isNaN(+A) || !B || isNaN(+B) || !rating || isNaN(+rating)) return fail(400);

		if (!thumbnail_source_id || isNaN(+thumbnail_source_id)) {
			return fail(400, { error: 'A thumbnail source must be selected' });
		}

		try {
			await client.POST('/api/work/merge', {
				fetch,
				params: {
					query: {
						from_work_id: +A,
						to_work_id: +B
					}
				},
				body: {
					title,
					description,
					thumbnail_source_id: +thumbnail_source_id,
					rating: +rating
				}
			});
			redirect(303, `/work/${+B!}`);
		} catch {
			return fail(400);
		}
	}
} satisfies Actions;
