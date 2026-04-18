import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { PathsApiCommentCommentsGetParametersQueryModel } from '$lib/schema';

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
					model: PathsApiCommentCommentsGetParametersQueryModel.account,
					pk: data.profile.id
				}
			}
		})
	]);

	// TODO: Error forwarding
	if (!comments) error(500, 'Failed to fetch data.');

	return { comments, connections };
};
