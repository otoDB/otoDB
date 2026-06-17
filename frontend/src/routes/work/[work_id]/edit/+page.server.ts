import client, { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const { data } = await client.GET('/api/work/sources', {
		params: {
			query: {
				work_id: params.work_id
			}
		},
		fetch
	});

	return {
		sources: data
	};
};

export const actions = {
	edit: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = data.get('title') as string,
			description = data.get('description') as string,
			rating = data.get('rating') as string,
			thumbnail_source_id = data.get('thumbnail_source') as string,
			reason = data.get('reason') as string;

		const { error: apiError } = await rawClient.PUT('/api/work/work', {
			fetch,
			params: {
				query: {
					work_id: params.work_id!,
					reason
				}
			},
			body: {
				title,
				description,
				rating: +rating,
				thumbnail_source_id: thumbnail_source_id || null
			}
		});
		if (apiError)
			return apiFail(apiError, {
				title,
				description,
				rating,
				thumbnail_source_id,
				reason
			});
		redirect(303, `/work/${params.work_id}`);
	},
	wiki_page: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const pages: { lang: number; md: string }[] = JSON.parse(data.get('wiki_pages') as string);
		if (pages.length === 0) {
			redirect(303, `/work/${params.work_id}`);
		}
		await client.POST('/api/wiki/work', {
			fetch,
			params: { query: { work_id: params.work_id! } },
			body: pages
		});
		redirect(303, `/work/${params.work_id}`);
	}
} satisfies Actions;
