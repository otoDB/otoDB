import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, parent, params }) => {
	const data = await parent();

	const [{ data: connections }, { data: comments }] = await Promise.all([
		client.GET('/api/profile/connection', {
			fetch,
			params: {
				query: {
					username: params.username
				}
			}
		}),
		client.GET('/api/comment/comments', {
			fetch,
			params: { query: { model: 'account', pk: data.profile.id } }
		})
	]);

	return { comments, connections };
};
