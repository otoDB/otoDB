import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { PathsApiCommentCommentsGetParametersQueryModel } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const [{ data: sources }, { data: comments }, { data: similar }] = await Promise.all([
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
			params: {
				query: {
					model: PathsApiCommentCommentsGetParametersQueryModel.mediawork,
					pk: +params.work_id
				}
			}
		}),
		client.GET('/api/work/similar', {
			fetch,
			params: { query: { work_id: +params.work_id } }
		})
	]);

	return {
		sources: sources,
		comments: comments,
		similar: similar
	};
};
