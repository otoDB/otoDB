import type { PageServerLoad } from './$types';
import client from '$lib/api.server';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data } = await client.GET('/api/work/relations', {
		params: {
			query: {
				work_id: params.work_id
			}
		},
		fetch
	});

	const [relations, works] = data!;
	if (relations.length === 0) return;

	return {
		works,
		relations
	};
};
