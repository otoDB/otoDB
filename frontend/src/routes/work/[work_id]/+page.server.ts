import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const [{ data: sources }, { data: comments }, { data: similar }] = await Promise.all([
		client.GET('/api/work/sources', {
			params: {
				query: {
					work_id: +params.work_id
				}
			},
			fetch
		}),
		client.GET('/api/comment/comments', {
			fetch,
			params: { query: { model: 'mediawork', pk: +params.work_id } }
		}),
		client.GET('/api/work/similar', {
			fetch,
			params: { query: { work_id: +params.work_id } }
		})
	]);

	if (!comments) error(500, 'Failed to load comments');

	return {
		sources: sources,
		comments: comments,
		similar: similar
	};
};
