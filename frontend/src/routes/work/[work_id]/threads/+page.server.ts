import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { PathsApiPostThreadsGetParametersQueryEntity } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const { data } = await client.GET('/api/post/threads', {
		fetch,
		params: {
			query: {
				entity: PathsApiPostThreadsGetParametersQueryEntity.mediawork,
				id: params.work_id,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});

	// TODO: Error forwarding
	return {
		threads: data,
		batch_size,
		page
	};
};
