import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

export const load: PageServerLoad = async ({ fetch, params, locals, url }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);

	const sourceId = +params.source_id;
	if (isNaN(sourceId)) error(400, { message: 'Bad request' });

	const [{ data: source, error: sourceError }, { data: suggestions }] = await Promise.all([
		client.GET('/api/source/source', {
			fetch,
			params: { query: { source_id: sourceId } }
		}),
		client.GET('/api/source/suggestions', {
			fetch,
			params: { query: { source_id: sourceId } }
		})
	]);

	if (sourceError) error(404, { message: 'Source not found' });

	return {
		source,
		suggestions,
		head: {
			title: `Review: ${source.title || 'Source #' + sourceId}`
		}
	};
};

export const actions = {
	create: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const title = data.get('title') as string;
		const description = data.get('description') as string;
		const rating = +(data.get('rating') as string) || 0;
		const tagsRaw = data.get('tags') as string;
		const tags = tagsRaw ? tagsRaw.split(' ').filter(Boolean) : [];

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
			return { failed: true, message: 'Failed to create work' };
		}

		redirect(303, `/work/${workId}`);
	},
	bind: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const workId = +(data.get('work_id') as string);
		const sourceUrl = data.get('source_url') as string;
		if (isNaN(workId)) return { failed: true, message: 'Invalid work ID' };

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
			return { failed: true, message: 'Failed to bind source to work' };
		}

		redirect(303, `/work/${workId}`);
	}
} satisfies Actions;
