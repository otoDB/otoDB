import { fail, redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import client from '$lib/api.server';
import { userLevelGuard } from '$lib/route_guard';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, params, locals, url, parent }) => {
	const sourceId = +params.source_id;
	const { source } = (await parent()) as any;

	// Only fetch suggestions for unbound sources (needed for work creation)
	let suggestions = null;
	if (!source.media) {
		userLevelGuard(locals.user, Levels.Member, url.pathname);
		const { data: s } = await client.GET('/api/upload/suggestions', {
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

		let workId: number | null = null;
		try {
			({ data: workId } = await client.POST('/api/work/create', {
				fetch,
				body: {
					source_id: +params.source_id,
					title: title || null,
					description: description || null,
					rating,
					tags
				}
			}));
		} catch {
			return fail(400, { failed: true, message: 'Failed to create work' });
		}

		redirect(303, `/work/${workId}`);
	},
	bind: async ({ request, fetch }) => {
		const data = await request.formData();
		const workId = +(data.get('work_id') as string);
		const sourceUrl = data.get('source_url') as string;
		if (isNaN(workId)) return { failed: true, message: 'Invalid work ID' };

		try {
			await client.POST('/api/upload/source', {
				fetch,
				params: {
					query: {
						url: sourceUrl,
						is_reupload: false,
						work_id: workId
					}
				}
			});
		} catch {
			return fail(400, { failed: true, message: 'Failed to bind source to work' });
		}

		redirect(303, `/work/${workId}`);
	}
} satisfies Actions;
