import client from '$lib/api.server';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data: wiki_page } = await client.GET('/api/wiki/work/{work_id}', {
		fetch,
		params: { path: { work_id: params.work_id } }
	});

	return {
		work_id: params.work_id,
		wiki_page: wiki_page ?? []
	};
};
