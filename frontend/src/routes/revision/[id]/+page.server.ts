import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const revision_id = +params.id;
	if (isNaN(revision_id)) error(400, { message: 'Bad request' });
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const batch_size = 30;

	const { data: changes } = await client.GET('/api/history/revision_changes', {
		fetch,
		params: {
			query: {
				revision_id,
				limit: batch_size,
				offset: batch_size * (page - 1)
			}
		}
	});

	return { changes, page, batch_size };
};
