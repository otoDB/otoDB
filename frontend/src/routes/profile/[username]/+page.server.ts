import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { ModelsWithComments } from '$lib/schema';

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
			params: {
				query: {
					model: ModelsWithComments.account,
					pk: +data.profile.id
				}
			}
		})
	]);

	return { comments, connections };
};
