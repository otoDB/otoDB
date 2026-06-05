import { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Mod, url.pathname);
};

export const actions = {
	default: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = (data.get('title') as string) || undefined;
		const pages: { lang: number; md: string }[] = JSON.parse(data.get('wiki_pages') as string);

		const { error: apiError } = await rawClient.POST('/api/wiki/{page_slug}', {
			fetch,
			params: {
				path: { page_slug: params.page_slug! },
				query: title ? { title } : {}
			},
			body: pages
		});
		if (apiError) return apiFail(apiError);
		redirect(303, `/wiki/${params.page_slug}`);
	}
} satisfies Actions;
