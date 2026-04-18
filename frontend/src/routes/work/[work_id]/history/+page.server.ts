import client from '$lib/api';
import type { PageServerLoad } from './$types';
import { PathsApiHistoryHistoryGetParametersQueryEntity } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: PathsApiHistoryHistoryGetParametersQueryEntity.mediawork,
				id: +params.work_id
			}
		}
	});

	return {
		history
	};
};
