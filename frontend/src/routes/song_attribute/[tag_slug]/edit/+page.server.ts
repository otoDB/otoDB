import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const category = data.get('category') as string,
			parent_slug = data.get('parent') as string;

		const { error } = await client.PUT('/api/tag/song_tag', {
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

		if (error) return fail(400, { category, parent_slug, failed: true });

		redirect(303, `/song_attribute/${params.tag_slug}`);
	}
} satisfies Actions;
