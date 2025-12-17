import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const [{ data }, { data: comments }] = await Promise.all([
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
		})
	]);

	const similar = client
		.GET('/api/work/similar', {
			fetch,
			params: { query: { work_id: +params.work_id } }
		})
		.then((res) => res.data);

	return {
		sources: data,
		comments,
		similar
	};
};
