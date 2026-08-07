import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { ModelsWithComments } from '$lib/schema';

export const load: PageServerLoad = async ({ fetch, parent, params }) => {
	const data = await parent();

	const [{ data: connections }, { data: comments }, { data: activity }] = await Promise.all([
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
					pk: data.profile.id
				}
			}
		}),
		client.GET('/api/profile/activity', {
			fetch,
			params: {
				query: {
					username: params.username
				}
			}
		})
	]);

	return { activity, comments, connections };
};
