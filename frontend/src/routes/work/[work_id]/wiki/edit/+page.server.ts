import client, { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const { data: wiki_page } = await client.GET('/api/wiki/work/{work_id}', {
		fetch,
		params: { path: { work_id: params.work_id } }
	});

	return {
		work_id: params.work_id,
		wiki_page: wiki_page ?? []
	};
};

export const actions = {
	default: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const pages: { lang: number; md: string }[] = JSON.parse(data.get('wiki_pages') as string);

		const { error: apiError } = await rawClient.POST('/api/wiki/work/{work_id}', {
			fetch,
			params: { path: { work_id: params.work_id! } },
			body: pages
		});
		if (apiError) return apiFail(apiError);
		redirect(303, `/work/${params.work_id}/wiki`);
	}
} satisfies Actions;
