import { redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch, params, locals, url, parent }) => {
	const sourceId = +params.source_id;
	const { source } = (await parent()) as any;

	// Only fetch suggestions for unbound sources (needed for work creation)
	let suggestions = null;
	if (!source.media) {
		userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);
		const { data: s } = await client.GET('/api/source/suggestions', {
			fetch,
			params: { query: { source_id: sourceId } }
		});
		suggestions = s;
	}

	return {
		suggestions,
		isBound: !!source.media
	};
};

export const actions = {
	create: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = data.get('title') as string;
		const description = data.get('description') as string;
		const rating = +(data.get('rating') as string) || 0;
		const tagsJsonRaw = data.get('tags_json') as string;
		const tags = tagsJsonRaw ? JSON.parse(tagsJsonRaw) : [];

		const { data: workId, error: createError } = await client.POST('/api/work/create', {
			fetch,
			body: {
				source_id: +params.source_id,
				title: title || null,
				description: description || null,
				rating,
				tags
			}
		});

		if (createError) {
			return { failed: true, message: m.cool_same_polecat_climb() };
		}

		redirect(303, `/work/${workId}`);
	},
	bind: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const workId = +(data.get('work_id') as string);
		const sourceUrl = data.get('source_url') as string;
		if (isNaN(workId)) return { failed: true, message: m.aloof_nice_bear_bask() };

		const { error: bindError } = await client.POST('/api/source/source', {
			fetch,
			params: {
				query: {
					url: sourceUrl,
					is_reupload: false,
					work_id: workId
				}
			}
		});

		if (bindError) {
			return { failed: true, message: m.trite_crazy_walrus_charm() };
		}

		redirect(303, `/work/${workId}`);
	}
} satisfies Actions;
