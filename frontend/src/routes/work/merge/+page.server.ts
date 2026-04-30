import { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { m } from '$lib/paraglide/messages';
import { userLevelGuard } from '$lib/route_guard';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Editor, url.pathname);
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

		if (!A || !B || !rating || isNaN(+rating)) return apiFail({ code: -1 });

		if (!thumbnail_source_id || isNaN(+thumbnail_source_id)) return apiFail({ code: -1 });

		const { error: apiError } = await rawClient.POST('/api/work/merge', {
			fetch,
			params: {
				query: {
					from_work_id: A,
					to_work_id: B
				}
			},
			body: {
				title,
				description,
				thumbnail_source_id,
				rating: +rating
			}
		});
		if (apiError) return apiFail(apiError);
		redirect(303, `/work/${B}`);
	}
} satisfies Actions;
