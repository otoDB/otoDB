import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, UserLevel.EDITOR, url.pathname);
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

		const { error } = await client.POST('/api/work/merge', {
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
		if (error) return fail(400);

		redirect(303, `/work/${+B!}`);
	}
} satisfies Actions;
