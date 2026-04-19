import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, locals, url }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const { data } = await client.GET('/api/work/sources', {
		params: {
			query: {
				work_id: +params.work_id
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

		const { error } = await client.PUT('/api/work/work', {
			fetch,
			params: {
				query: {
					work_id: +params.work_id!,
					reason
				}
			},
			body: {
				title,
				description,
				rating: +rating,
				thumbnail_source_id: thumbnail_source_id ? +thumbnail_source_id : null
			}
		});

		if (error)
			return fail(400, {
				title,
				description,
				rating,
				thumbnail_source_id,
				reason,
				failed: true
			});
		redirect(303, `/work/${params.work_id}`);
	}
} satisfies Actions;
