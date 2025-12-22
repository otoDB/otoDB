import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const revision_id = +params.id;
	if (isNaN(revision_id)) error(400, { message: 'Bad request' });
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const batch_size = 30;

	const [{ data: changes }, { data: revision }] = await Promise.all([
		client.GET('/api/history/revision_changes', {
			fetch,
			params: {
				query: {
					revision_id,
					limit: batch_size,
					offset: batch_size * (page - 1)
				}
			}
		}),
		client.GET('/api/history/revision', { fetch, params: { query: { revision_id } } })
	]);

	if (!revision) error(404, { message: 'Not found' });

	return {
		revision,
		changes,
		page,
		batch_size
	};
};
