import { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const category = data.get('category') as string,
			parent_slug = data.get('parent') as string;

		const { error: apiError } = await rawClient.PUT('/api/tag/song_tag', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug!
				}
			},
			body: {
				category: +category,
				parent_slug
			}
		});
		if (apiError) return apiFail(apiError, { category, parent_slug });

		redirect(303, `/song_attribute/${encodeURIComponent(params.tag_slug!)}`);
	}
} satisfies Actions;
