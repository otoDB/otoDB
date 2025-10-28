import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const revision_id = +params.id;
    if (isNaN(revision_id)) error(400, { message: 'Bad request' });

	const { data } = await client.GET('/api/history/revision', {
		fetch,
		params: {
			query: {
                revision_id
			}
		}
	});

	return {
		revision: data
	};
};
