import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { PathsApiCommentCommentsGetParametersQueryModel } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, params, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const [{ data: entries }, { data: comments }, { data: pending_items }] = await Promise.all([
		client.GET('/api/list/entries', {
			fetch,
			params: {
				query: {
					list_id: +params.list_id,
					limit: batch_size,
					offset: (page - 1) * batch_size
				}
			}
		}),
		client.GET('/api/comment/comments', {
			params: {
				query: {
					pk: +params.list_id,
					model: PathsApiCommentCommentsGetParametersQueryModel.pool
				}
			},
			fetch
		}),
		client.GET('/api/list/pending', {
			fetch,
			params: { query: { list_id: +params.list_id, limit: batch_size, offset: 0 } }
		})
	]);

	// TODO: Error forwarding
	if (!entries) error(500, 'Failed to fetch data.');
	if (!comments) error(500, 'Failed to fetch comments.');

	return { entries, comments, pending_items, batch_size, page };
};
